from database.connection import get_connection


def search_trains(source: str, destination: str):
    """Return trains between selected source and destination."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # fetch trains matching source + destination
    sql = """
        SELECT
            t.train_id,
            t.name AS train_name,
            r.route_id,
            s1.station_name AS source,
            s2.station_name AS destination,
            r.distance_km,
            r.duration
        FROM train t
        JOIN route r   ON t.route_id = r.route_id
        JOIN station s1 ON r.source_id = s1.station_id
        JOIN station s2 ON r.destination_id = s2.station_id
        WHERE s1.station_name = %s
          AND s2.station_name = %s
    """
    cur.execute(sql, (source, destination))
    rows = cur.fetchall()

    result = []

    # add seat + fare details
    for r in rows:
        tid = r["train_id"]
        rid = r["route_id"]

        # seat capacity
        cur.execute(
            "SELECT seat_type, total_seats FROM train_capacity WHERE train_id=%s",
            (tid,)
        )
        caps = cur.fetchall()

        seats = {"GENERAL": 0, "SLEEPER": 0, "AC": 0}
        for c in caps:
            seats[c["seat_type"]] = c["total_seats"]

        # fare for each seat
        def get_fare(stype):
            cur.execute("SELECT calculate_fare(%s,%s,1) AS f", (rid, stype))
            return float(cur.fetchone()["f"])

        result.append({
            **r,
            "general_seats": seats["GENERAL"],
            "sleeper_seats": seats["SLEEPER"],
            "ac_seats": seats["AC"],
            "general_fare": get_fare("GENERAL"),
            "sleeper_fare": get_fare("SLEEPER"),
            "ac_fare": get_fare("AC"),
        })

    cur.close()
    conn.close()
    return result
