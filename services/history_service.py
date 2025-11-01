from database.connection import get_connection


def get_history(passenger_id):
    """Return booking history for a passenger."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT
            b.booking_id,
            b.pnr,
            b.travel_date,
            b.status,
            b.seat_type,
            b.passenger_count,
            t.name AS train_name,
            calculate_fare(b.route_id, b.seat_type, b.passenger_count) AS total_fare,
            (
                SELECT amount
                FROM payment p
                WHERE p.booking_id = b.booking_id
                ORDER BY payment_id DESC
                LIMIT 1
            ) AS last_payment,
            b.cancel_time
        FROM booking b
        JOIN train t ON t.train_id = b.train_id
        WHERE b.passenger_id = %s
        ORDER BY b.booking_id DESC
    """

    cur.execute(sql, (passenger_id,))
    rows = cur.fetchall()

    # normalizing numeric output
    for r in rows:
        r["total_fare"]   = float(r["total_fare"] or 0)
        r["last_payment"] = float(r["last_payment"]) if r["last_payment"] else None

    cur.close()
    conn.close()
    return rows
