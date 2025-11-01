"""
EMPLOYEE SERVICE
All database-access functions required for EMPLOYEE module.
"""

from database.connection import get_connection
from typing import Optional, List, Dict


# =====================================================
#  PROFILE
# =====================================================
def get_employee_profile(emp_id: int):
    """
    Returns full employee record for given employee ID.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM employee WHERE emp_id=%s", (emp_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    return row


# =====================================================
# TRAINS — detailed list (with route)
# =====================================================
def list_all_trains_with_route():
    """
    List all trains along with route details (source, destination, distance, duration).
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            t.train_id,
            t.name AS train_name,
            t.status,
            s1.station_name AS source,
            s2.station_name AS destination,
            r.distance_km,
            r.duration
        FROM train t
        LEFT JOIN route  r  ON t.route_id = r.route_id
        LEFT JOIN station s1 ON r.source_id = s1.station_id
        LEFT JOIN station s2 ON r.destination_id = s2.station_id
        ORDER BY t.train_id;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# =====================================================
# TRAINS — basic list (id + name only)
# =====================================================
def list_trains_basic():
    """
    Returns only train_id + train name (for dropdowns).
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT train_id, name FROM train ORDER BY train_id")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# =====================================================
# BOOKINGS — per train
# =====================================================
def list_bookings_for_train(train_id: int):
    """
    Get all bookings for a specific train.
    Includes passenger name & basic ticket details.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            b.booking_id, b.pnr, b.travel_date, b.seat_type,
            b.passenger_count, b.status,
            p.first_name, p.last_name
        FROM booking b
        JOIN passenger p 
              ON p.passenger_id = b.passenger_id
        WHERE b.train_id = %s
        ORDER BY b.travel_date DESC, b.booking_id DESC;
    """, (train_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# =====================================================
# SEAT CAPACITY — get
# =====================================================
def get_train_seat_capacity(train_id: int):
    """
    Returns dict: { 'GENERAL': X, 'SLEEPER': Y, 'AC': Z }
    Missing types default to 0.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT seat_type, total_seats
        FROM train_capacity
        WHERE train_id=%s
    """, (train_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # default values
    base = {"GENERAL": 0, "SLEEPER": 0, "AC": 0}
    for r in rows:
        base[r["seat_type"]] = r["total_seats"]

    return base


# =====================================================
# SEAT CAPACITY — insert or update
# =====================================================
def upsert_train_seat_capacity(train_id: int, seat_type: str, total_seats: int):
    """
    Insert or update seat capacity for train.
    ON DUPLICATE KEY → updates instead of inserting new row.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO train_capacity (train_id, seat_type, total_seats)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE total_seats = VALUES(total_seats)
    """, (train_id, seat_type, total_seats))

    conn.commit()
    cur.close()
    conn.close()


# =====================================================
# TRAIN STATUS
# =====================================================
def update_train_status(train_id: int, status: str):
    """
    Update train current status: ON-TIME / DELAYED / CANCELLED.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE train
        SET status = %s
        WHERE train_id = %s
    """, (status, train_id))

    conn.commit()
    cur.close()
    conn.close()


# =====================================================
# ASSIGNMENTS — list
# =====================================================
def list_assignments_for_employee(emp_id: int) -> List[Dict]:
    """
    Returns past + present train assignments for this employee.
    Includes:
      - Train
      - Who assigned
      - When assigned
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            a.id,
            t.train_id,
            t.name AS train_name,
            a.assigned_at,
            ab.first_name AS assigned_by_first, 
            ab.last_name  AS assigned_by_last
        FROM employee_train_assignment a
        JOIN train t 
            ON t.train_id = a.train_id
        LEFT JOIN employee ab 
            ON ab.emp_id = a.assigned_by
        WHERE a.emp_id = %s
        ORDER BY a.assigned_at DESC, t.train_id
    """, (emp_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# =====================================================
# SCHEDULE
# =====================================================
def list_schedule_for_employee(
        emp_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
    """
    List work schedule for employee.
    Optional: filter by date range (YYYY-MM-DD).
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    base = """
        SELECT 
            w.shift_id,
            w.shift_date,
            w.start_time,
            w.end_time,
            w.role_on_shift,
            w.notes,
            t.train_id,
            t.name AS train_name
        FROM work_schedule w
        LEFT JOIN train t 
            ON t.train_id = w.train_id
        WHERE w.emp_id = %s
    """
    params = [emp_id]

    # optional filters
    if date_from and date_to:
        base += " AND w.shift_date BETWEEN %s AND %s"
        params += [date_from, date_to]
    elif date_from:
        base += " AND w.shift_date >= %s"
        params.append(date_from)
    elif date_to:
        base += " AND w.shift_date <= %s"
        params.append(date_to)

    base += " ORDER BY w.shift_date ASC, w.start_time ASC"

    cur.execute(base, tuple(params))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# =====================================================
# REPORT TO SUPERVISOR
# =====================================================
def create_report_to_supervisor(emp_id: int, subject: str, message: str) -> int:
    """
    Submit a report → linked to the employee's supervisor.
    Returns newly inserted report ID.
    """
    conn = get_connection()
    cur = conn.cursor()

    # find supervisor
    cur.execute("SELECT supervisor_id FROM employee WHERE emp_id=%s", (emp_id,))
    row = cur.fetchone()

    if not row or row[0] is None:
        cur.close()
        conn.close()
        raise ValueError("Supervisor not linked for this employee.")

    supervisor_id = int(row[0])

    cur.execute("""
        INSERT INTO supervisor_report (emp_id, supervisor_id, subject, message)
        VALUES (%s, %s, %s, %s)
    """, (emp_id, supervisor_id, subject, message))

    conn.commit()
    report_id = cur.lastrowid

    cur.close()
    conn.close()
    return report_id


# =====================================================
# MY REPORT LIST
# =====================================================
def list_my_reports(emp_id: int) -> List[Dict]:
    """
    Shows reports submitted by employee (latest first).
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            report_id,
            subject,
            message,
            status,
            created_at
        FROM supervisor_report
        WHERE emp_id = %s
        ORDER BY created_at DESC
    """, (emp_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows
