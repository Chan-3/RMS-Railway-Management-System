"""
admin_service.py
----------------
Service layer (core business logic) for ADMIN operations.

Covers:
✔ Trains
✔ Stations
✔ Routes
✔ Passengers
✔ Employees
✔ Reports (Revenue / Bookings / Assignments)

Each function only handles DB query + basic logic.
No HTML, redirects, or request objects appear here.

Uses: get_connection() → connects to DB
"""

from typing import Optional, List, Dict, Tuple
from werkzeug.security import generate_password_hash
from database.connection import get_connection
from mysql.connector import IntegrityError


# =====================================================================
#  TRAINS  (train table stores train name, route + status)
# =====================================================================

def list_trains_with_route() -> List[Dict]:
    """
    Returns train + route + source & destination station
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.train_id, t.name AS train_name, t.status,
               r.route_id,
               s1.station_name AS source,
               s2.station_name AS destination
        FROM train t
        LEFT JOIN route r ON t.route_id = r.route_id
        LEFT JOIN station s1 ON r.source_id = s1.station_id
        LEFT JOIN station s2 ON r.destination_id = s2.station_id
        ORDER BY t.train_id
    """)

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_train(train_id: int) -> Optional[Dict]:
    """Fetch one train by ID"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.train_id, t.name, t.status, t.route_id
        FROM train t
        WHERE t.train_id=%s
    """, (train_id,))

    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def create_train(name: str, route_id: int, status: str = "ON-TIME"):
    """Create train"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO train (name, route_id, status)
        VALUES (%s, %s, %s)
    """, (name, route_id, status))

    conn.commit()
    cur.close(); conn.close()


def update_train(train_id: int, name: str, route_id: int, status: str):
    """Update train"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE train
        SET name=%s, route_id=%s, status=%s
        WHERE train_id=%s
    """, (name, route_id, status, train_id))

    conn.commit()
    cur.close(); conn.close()


def delete_train(train_id: int):
    """Delete train"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM train WHERE train_id=%s", (train_id,))
    conn.commit()
    cur.close(); conn.close()


# =====================================================================
#  STATIONS (station table holds station names)
# =====================================================================

def list_stations() -> List[Dict]:
    """Get all stations sorted by name"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT station_id, station_name
        FROM station
        ORDER BY station_name
    """)

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_station(station_id: int) -> Optional[Dict]:
    """Fetch station by ID"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT station_id, station_name
        FROM station
        WHERE station_id=%s
    """, (station_id,))

    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def create_station(station_name: str):
    """Add new station"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO station (station_name)
        VALUES (%s)
    """, (station_name,))

    conn.commit()
    cur.close(); conn.close()


def update_station(station_id: int, station_name: str):
    """Rename a station"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE station
        SET station_name=%s
        WHERE station_id=%s
    """, (station_name, station_id))

    conn.commit()
    cur.close(); conn.close()


def delete_station(station_id: int):
    """
    Delete station only if not used in route
    (protecting DB consistency)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Check references in route
    cur.execute("""
        SELECT COUNT(*)
        FROM route
        WHERE source_id=%s OR destination_id=%s
    """, (station_id, station_id))

    (count,) = cur.fetchone()

    if count > 0:
        cur.close(); conn.close()
        return False, "Station is used in routes — delete route first."

    # Safe to delete
    cur.execute("""
        DELETE FROM station
        WHERE station_id=%s
    """, (station_id,))

    conn.commit()
    cur.close(); conn.close()
    return True, "Station deleted."


# =====================================================================
#  ROUTES (route table links source + destination + distance)
# =====================================================================

def list_routes_full() -> List[Dict]:
    """List all routes + station names"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT r.route_id, r.distance_km, r.duration,
               s1.station_id AS source_id,
               s1.station_name AS source,
               s2.station_id AS destination_id,
               s2.station_name AS destination
        FROM route r
        JOIN station s1 ON r.source_id = s1.station_id
        JOIN station s2 ON r.destination_id = s2.station_id
        ORDER BY r.route_id
    """)

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_route(route_id: int) -> Optional[Dict]:
    """Get route details"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT route_id, distance_km, duration, source_id, destination_id
        FROM route
        WHERE route_id=%s
    """, (route_id,))

    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def create_route(source_id: int, destination_id: int, distance_km: float, duration: str):
    """Add new route"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO route (source_id, destination_id, distance_km, duration)
        VALUES (%s, %s, %s, %s)
    """, (source_id, destination_id, distance_km, duration))

    conn.commit()
    cur.close(); conn.close()


def update_route(route_id: int, source_id: int, destination_id: int, distance_km: float, duration: str):
    """Modify route"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE route
        SET source_id=%s, destination_id=%s, distance_km=%s, duration=%s
        WHERE route_id=%s
    """, (source_id, destination_id, distance_km, duration, route_id))

    conn.commit()
    cur.close(); conn.close()


def delete_route(route_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM route WHERE route_id=%s", (route_id,))
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()



# =====================================================================
#  PASSENGERS (Basic CRUD + activate)
# =====================================================================

def list_passengers(q: str = "") -> List[Dict]:
    """
    Search passengers by name or email
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT passenger_id, first_name, last_name, email,
               COALESCE(active, 1) AS active
        FROM passenger
    """
    params = []

    if q:
        sql += " WHERE first_name LIKE %s OR last_name LIKE %s OR email LIKE %s"
        like = f"%{q}%"
        params = [like, like, like]

    sql += " ORDER BY passenger_id DESC"

    cur.execute(sql, tuple(params))

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def delete_passenger(passenger_id: int):
    """Remove passenger"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM passenger
        WHERE passenger_id=%s
    """, (passenger_id,))

    conn.commit()
    cur.close(); conn.close()


def set_passenger_active(passenger_id: int, active: int):
    """
    Enable / Disable passenger (active flag = 1/0)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Create column only once (safe)
    try:
        cur.execute("""
            ALTER TABLE passenger
            ADD COLUMN IF NOT EXISTS active TINYINT(1) DEFAULT 1
        """)
    except:
        pass

    cur.execute("""
        UPDATE passenger
        SET active=%s
        WHERE passenger_id=%s
    """, (active, passenger_id))

    conn.commit()
    cur.close(); conn.close()


# =====================================================================
#  EMPLOYEES (via Admin only)
# =====================================================================

def list_employees_all(q: str = "", role_filter: Optional[str] = None) -> List[Dict]:
    """
    Admin view — search employees + filter by role
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id
        FROM employee
        WHERE 1=1
    """
    params = []

    if role_filter:
        sql += " AND role=%s"
        params.append(role_filter)

    if q:
        like = f"%{q}%"
        sql += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
        params += [like, like, like]

    sql += " ORDER BY emp_id DESC"

    cur.execute(sql, tuple(params))

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_employee(emp_id: int) -> Optional[Dict]:
    """Fetch employee by ID"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id
        FROM employee
        WHERE emp_id=%s
    """, (emp_id,))

    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def create_employee_admin(first_name, last_name, email, role, salary, supervisor_id):
    """
    Create employee with default temporary password
    (Admin assigns real password later)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO employee (first_name, last_name, email, role, salary, password, supervisor_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        first_name, last_name, email, role, salary,
        generate_password_hash("Temp@123"),
        supervisor_id
    ))

    conn.commit()
    cur.close(); conn.close()


def update_employee_admin(emp_id, role, salary, supervisor_id):
    """Modify employee"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE employee
        SET role=%s, salary=%s, supervisor_id=%s
        WHERE emp_id=%s
    """, (role, salary, supervisor_id, emp_id))

    conn.commit()
    cur.close(); conn.close()


def set_employee_active(emp_id: int, active: int):
    """
    Enable / Disable employee (active=1/0)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Add column if missing
    try:
        cur.execute("""
            ALTER TABLE employee
            ADD COLUMN IF NOT EXISTS active TINYINT(1) DEFAULT 1
        """)
    except:
        pass

    cur.execute("""
        UPDATE employee
        SET active=%s
        WHERE emp_id=%s
    """, (active, emp_id))

    conn.commit()
    cur.close(); conn.close()


# =====================================================================
#  REPORTS
# =====================================================================

def revenue_report(date_from=None, date_to=None, train_id=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT
            b.travel_date,
            t.name AS train_name,
            COUNT(b.booking_id) AS bookings,
            COALESCE(SUM(p.amount), 0) AS revenue
        FROM booking b
        JOIN train t   ON b.train_id = t.train_id
        LEFT JOIN payment p ON b.booking_id = p.booking_id
        WHERE 1=1
    """
    params = []

    if date_from:
        sql += " AND b.travel_date >= %s"
        params.append(date_from)

    if date_to:
        sql += " AND b.travel_date <= %s"
        params.append(date_to)

    if train_id:
        sql += " AND b.train_id = %s"
        params.append(train_id)

    sql += """
        GROUP BY b.travel_date, t.name
        ORDER BY b.travel_date DESC
    """

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()

    total = sum(r["revenue"] or 0 for r in rows)

    cur.close()
    conn.close()
    return rows, total



def bookings_report(date_from, date_to, train_id) -> List[Dict]:
    """
    Report →
    All bookings + passenger name + train
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT b.booking_id, b.pnr, b.travel_date, b.seat_type,
               b.passenger_count, b.status,
               t.name AS train_name,
               p.first_name, p.last_name
        FROM booking b
        JOIN train t     ON t.train_id = b.train_id
        JOIN passenger p ON p.passenger_id = b.passenger_id
        WHERE 1=1
    """

    params = []

    if date_from and date_to:
        sql += " AND b.travel_date BETWEEN %s AND %s"
        params += [date_from, date_to]
    elif date_from:
        sql += " AND b.travel_date >= %s"
        params.append(date_from)
    elif date_to:
        sql += " AND b.travel_date <= %s"
        params.append(date_to)

    if train_id:
        sql += " AND b.train_id=%s"
        params.append(train_id)

    sql += " ORDER BY b.travel_date DESC, b.booking_id DESC"

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()

    cur.close(); conn.close()
    return rows


def assignment_report() -> List[Dict]:
    """
    Shows → #employees assigned to each train
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.train_id,
               t.name AS train_name,
               COUNT(a.emp_id) AS assigned_employees
        FROM train t
        LEFT JOIN employee_train_assignment a
               ON a.train_id = t.train_id
        GROUP BY t.train_id, t.name
        ORDER BY t.train_id
    """)

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows
