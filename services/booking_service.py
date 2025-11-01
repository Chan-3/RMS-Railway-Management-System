from database.connection import get_connection


def create_booking(passenger_id, data):
    """
    Create a new booking via stored procedure.
    `data` must contain: train_id, route_id, travel_date, seat_type, count, payment_mode
    """
    required = ["train_id", "route_id", "travel_date", "seat_type", "count", "payment_mode"]
    for k in required:
        if not data.get(k):
            return {"ok": False, "error": f"Missing {k}"}

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Call stored procedure: create_booking(...) 
        args = [
            passenger_id,
            data["train_id"],
            data["route_id"],
            data["travel_date"],
            data["seat_type"],
            data["count"],
            0,   # OUT: booking_id
            "",  # OUT: PNR
            0.0  # OUT: total fare
        ]
        res = cur.callproc("create_booking", args)

        booking_id = res[6]
        pnr = res[7]
        total_fare = res[8]

        # Record payment
        cur.execute(
            """
            INSERT INTO payment (booking_id, amount, mode, status)
            VALUES (%s, %s, %s, 'SUCCESS')
            """,
            (booking_id, total_fare, data["payment_mode"])
        )
        conn.commit()

        cur.close()
        conn.close()
        return {
            "ok": True,
            "data": {
                "booking_id": booking_id,
                "pnr": pnr,
                "total_fare": total_fare
            }
        }

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return {"ok": False, "error": str(e)}


def cancel_booking(booking_id: int):
    """
    Cancel booking → calls stored procedure 'cancel_booking'
    Returns refund amount + percent if successful.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        args = [booking_id, 0.0, 0]   # OUT refund_amount, refund_percent
        res = cur.callproc("cancel_booking", args)

        refund_amount = res[1]
        refund_percent = res[2]

        conn.commit()
        cur.close()
        conn.close()

        return {
            "ok": True,
            "refund_amount": refund_amount,
            "refund_percent": refund_percent
        }

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return {"ok": False, "error": str(e)}
