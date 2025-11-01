/* =========================================================
   RMS • FUNCTIONS
   Deterministic helper functions for procedures/triggers
   Safe re-run: Drops existing functions before creation
========================================================= */

USE rms;

DELIMITER $$


/* -------------------------
   Drop existing functions
------------------------- */
DROP FUNCTION IF EXISTS calculate_fare $$
DROP FUNCTION IF EXISTS calculate_refund $$


/* =========================================================
   FUNCTION: calculate_fare(route_id, seat_type, passenger_count)
   Returns: distance_km × rate_per_km × passenger_count
   Reads:
     • route.distance_km
     • fare_rate.rate
========================================================= */
CREATE FUNCTION calculate_fare(
    p_route_id INT,
    p_seat_type ENUM('GENERAL','SLEEPER','AC'),
    p_passenger_count INT
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE v_distance INT;
    DECLARE v_rate     DECIMAL(5,2);
    DECLARE v_total    DECIMAL(10,2);

    -- Distance for route
    SELECT distance_km
      INTO v_distance
      FROM route
     WHERE route_id = p_route_id;

    -- Rate per seat type
    SELECT rate
      INTO v_rate
      FROM fare_rate
     WHERE seat_type = p_seat_type;

    -- Final fare
    SET v_total = v_distance * v_rate * p_passenger_count;
    RETURN v_total;
END $$
/* END FUNCTION: calculate_fare */



/* =========================================================
   FUNCTION: calculate_refund(booking_id)
   Logic:
     • Get passenger_id
     • Count existing cancellations today (excluding current)
     • Refund% = 100 − (count × 10)
     • Min = 0%
========================================================= */
CREATE FUNCTION calculate_refund(p_booking_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_passenger_id   INT;
    DECLARE v_prior_cancels  INT DEFAULT 0;
    DECLARE v_refund_percent INT;

    -- Resolve passenger
    SELECT passenger_id
      INTO v_passenger_id
      FROM booking
     WHERE booking_id = p_booking_id;

    -- Missing booking → full refund
    IF v_passenger_id IS NULL THEN
        RETURN 100;
    END IF;

    -- Previous cancellation count today
    SELECT COUNT(*)
      INTO v_prior_cancels
      FROM booking
     WHERE passenger_id = v_passenger_id
       AND status = 'CANCELLED'
       AND DATE(cancel_time) = CURDATE()
       AND booking_id <> p_booking_id;

    -- Compute refund
    SET v_refund_percent = 100 - (v_prior_cancels * 10);

    -- Clamp to 0%
    IF v_refund_percent < 0 THEN
        SET v_refund_percent = 0;
    END IF;

    RETURN v_refund_percent;
END $$
/* END FUNCTION: calculate_refund */


-- =========================================================
-- Add new functions below this line
-- =========================================================

DELIMITER ;
