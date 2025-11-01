/* =========================================================
   RMS • STORED PROCEDURES
   Transactional business logic (create / cancel booking)
   Re-run safe — old procedures dropped before creation
========================================================= */

USE rms;
DELIMITER $$


/* -------------------------
   Remove existing procedures
------------------------- */
DROP PROCEDURE IF EXISTS create_booking $$
DROP PROCEDURE IF EXISTS cancel_booking $$


/* =========================================================
   PROCEDURE: create_booking
   IN :
      passenger_id, train_id, route_id, travel_date,
      seat_type, passenger_count
   OUT:
      booking_id, pnr, total_fare

   Steps:
     1) Check seat availability
     2) Compute fare using calculate_fare()
     3) Insert CONFIRMED booking + PNR
     4) Reduce available seats
========================================================= */
CREATE PROCEDURE create_booking(
    IN  p_passenger_id INT,
    IN  p_train_id INT,
    IN  p_route_id INT,
    IN  p_travel_date DATE,
    IN  p_seat_type ENUM('GENERAL','SLEEPER','AC'),
    IN  p_passenger_count INT,
    OUT p_booking_id INT,
    OUT p_pnr VARCHAR(15),
    OUT p_total_fare DECIMAL(10,2)
)
BEGIN
    DECLARE v_available_seats INT;

    -- 1) Check seat availability
    SELECT total_seats
      INTO v_available_seats
      FROM train_capacity
     WHERE train_id = p_train_id
       AND seat_type = p_seat_type;

    IF v_available_seats IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid train_id or seat_type';
    END IF;

    IF v_available_seats < p_passenger_count THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Not enough seats available';
    END IF;

    -- 2) Calculate fare
    SET p_total_fare = calculate_fare(p_route_id, p_seat_type, p_passenger_count);

    -- 3) Create PNR + booking row
    SET p_pnr = CONCAT('PNR', FLOOR(RAND() * 900000 + 100000));

    INSERT INTO booking (
        passenger_id, train_id, route_id,
        travel_date, seat_type, passenger_count, pnr, status
    ) VALUES (
        p_passenger_id, p_train_id, p_route_id,
        p_travel_date, p_seat_type, p_passenger_count,
        p_pnr, 'CONFIRMED'
    );

    SET p_booking_id = LAST_INSERT_ID();

    -- 4) Reduce seats
    UPDATE train_capacity
       SET total_seats = total_seats - p_passenger_count
     WHERE train_id = p_train_id
       AND seat_type = p_seat_type;
END $$
/* END PROCEDURE: create_booking */



/* =========================================================
   PROCEDURE: cancel_booking
   IN : booking_id
   OUT: refund_amount, refund_percent

   Steps:
     1) Validate booking
     2) Get fare via calculate_fare()
     3) Get refund% via calculate_refund()
     4) Update booking → CANCELLED + cancel_time
     5) Log refund payment
     6) Restore seats
========================================================= */
CREATE PROCEDURE cancel_booking(
    IN  p_booking_id INT,
    OUT p_refund_amount DECIMAL(10,2),
    OUT p_refund_percent INT
)
BEGIN
    DECLARE v_passenger_id INT;
    DECLARE v_train_id INT;
    DECLARE v_route_id INT;
    DECLARE v_seat_type ENUM('GENERAL','SLEEPER','AC');
    DECLARE v_count INT;
    DECLARE v_total_fare DECIMAL(10,2);

    -- 1) Retrieve booking details
    SELECT passenger_id, train_id, route_id, seat_type, passenger_count
      INTO v_passenger_id, v_train_id, v_route_id, v_seat_type, v_count
      FROM booking
     WHERE booking_id = p_booking_id;

    IF v_passenger_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Booking not found';
    END IF;

    -- 2) Full fare for this booking
    SET v_total_fare = calculate_fare(v_route_id, v_seat_type, v_count);

    -- 3) Refund %
    SET p_refund_percent = calculate_refund(p_booking_id);

    -- 4) Refund amount
    SET p_refund_amount = (v_total_fare * p_refund_percent) / 100;

    -- Update booking
    UPDATE booking
       SET status      = 'CANCELLED',
           cancel_time = NOW()
     WHERE booking_id = p_booking_id;

    -- 5) Record refund entry
    INSERT INTO payment (booking_id, mode, amount, status)
    VALUES (p_booking_id, 'CASH', p_refund_amount, 'SUCCESS');

    -- 6) Return seats to capacity
    UPDATE train_capacity
       SET total_seats = total_seats + v_count
     WHERE train_id = v_train_id
       AND seat_type = v_seat_type;
END $$
/* END PROCEDURE: cancel_booking */


-- =========================================================
-- Add more procedures below
-- =========================================================

DELIMITER ;