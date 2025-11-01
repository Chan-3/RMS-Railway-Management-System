from typing import Optional, List, Dict
from werkzeug.security import generate_password_hash
from database.connection import get_connection

# ----------------------------------------------------
# Allowed non-supervisor employee roles
# ----------------------------------------------------
ALLOWED_STAFF_ROLES = [
    "EMPLOYEE",          # generic secondary worker
    "CLERK",
    "DRIVER",
    "GUARD",
    "TICKET_EXAMINER",
    "PORTER",
    "CLEANING_STAFF",
]


# ====================================================
# ✅ EMPLOYEES (ScopED Access)
# ====================================================
def list_employees(q: str = "", supervisor_scope_id: Optional[int] = None,
                   role_filter: Optional[str] = None) -> List[Dict]:
    """
    List employees under a supervisor.
    - Excludes supervisors.
    - Allows search + role filtering.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id, 1 AS active
        FROM employee
        WHERE role <> 'SUPERVISOR'
    """
    params = []

    if supervisor_scope_id:
        sql += " AND supervisor_id = %s"
        params.append(supervisor_scope_id)

    if q:
        like = f"%{q}%"
        sql += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
        params += [like, like, like]

    if role_filter and role_filter != "SUPERVISOR":
        sql += " AND role = %s"
        params.append(role_filter)

    sql += " ORDER BY emp_id"
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_employee_scoped(emp_id: int, supervisor_scope_id: int) -> Optional[Dict]:
    """Fetch employee data only if they report to this supervisor."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id, 1 AS active
        FROM employee
        WHERE emp_id=%s AND supervisor_id=%s AND role <> 'SUPERVISOR'
    """, (emp_id, supervisor_scope_id))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def create_employee_under_supervisor(supervisor_id: int, first_name: str, last_name: str,
                                     email: str, role: str, salary: float):
    """Create employee under supervisor. Temp password auto-assigned."""
    if not first_name or not last_name or not email or not role:
        raise ValueError("All fields are required.")
    if role not in ALLOWED_STAFF_ROLES:
        raise ValueError("Invalid role selected.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employee (first_name, last_name, email, role, salary, password, supervisor_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        first_name, last_name, email, role, salary,
        generate_password_hash("Temp@123"), supervisor_id
    ))
    conn.commit()
    cur.close(); conn.close()


def update_employee_core_scoped(emp_id: int, supervisor_scope_id: int, role: str,
                                salary: float) -> bool:
    """Update subordinate employee role + salary."""
    if role not in ALLOWED_STAFF_ROLES:
        raise ValueError("Invalid role selected.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE employee
        SET role=%s, salary=%s
        WHERE emp_id=%s AND supervisor_id=%s AND role <> 'SUPERVISOR'
    """, (role, salary, emp_id, supervisor_scope_id))
    conn.commit()
    updated = cur.rowcount > 0
    cur.close(); conn.close()
    return updated


# ====================================================
# ✅ ASSIGNMENTS (ScopED)
# ====================================================
def list_trains_basic() -> List[Dict]:
    """Return basic train info."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT train_id, name FROM train ORDER BY train_id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def list_assignments_for_emp(emp_id: int, supervisor_scope_id: int) -> List[Dict]:
    """Return employee train assignments within scope."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.emp_id, a.train_id, t.name AS train_name, a.assigned_at
        FROM employee_train_assignment a
        JOIN train t ON t.train_id = a.train_id
        JOIN employee e ON e.emp_id = a.emp_id
        WHERE a.emp_id=%s AND e.supervisor_id=%s
        ORDER BY a.assigned_at DESC
    """, (emp_id, supervisor_scope_id))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def assign_emp_to_train_scoped(emp_id: int, train_id: int, supervisor_scope_id: int):
    """Assign employee to train if under supervisor."""
    conn = get_connection()
    cur = conn.cursor()

    # Verify scope
    cur.execute("SELECT 1 FROM employee WHERE emp_id=%s AND supervisor_id=%s",
                (emp_id, supervisor_scope_id))
    ok = cur.fetchone()
    if not ok:
        cur.close(); conn.close()
        raise PermissionError("Not allowed – employee not under this supervisor.")

    cur.execute("""
        INSERT INTO employee_train_assignment (emp_id, train_id, assigned_by)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE assigned_at = assigned_at
    """, (emp_id, train_id, supervisor_scope_id))

    conn.commit()
    cur.close(); conn.close()


def remove_assignment_scoped(emp_id: int, train_id: int, supervisor_scope_id: int):
    """Remove assignment only if subordinate."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM employee WHERE emp_id=%s AND supervisor_id=%s",
                (emp_id, supervisor_scope_id))
    ok = cur.fetchone()
    if not ok:
        cur.close(); conn.close()
        raise PermissionError("Not allowed – employee not under this supervisor.")

    cur.execute("""
        DELETE FROM employee_train_assignment WHERE emp_id=%s AND train_id=%s
    """, (emp_id, train_id))
    conn.commit()
    cur.close(); conn.close()


# ====================================================
# ✅ SHIFTS / SCHEDULE
# ====================================================
def list_schedule_for_employee(emp_id: Optional[int], supervisor_scope_id: int,
                               date_from: Optional[str], date_to: Optional[str]) -> List[Dict]:
    """Return schedule only for supervised employee."""
    if not emp_id:
        return []

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT w.shift_id, w.shift_date, w.start_time, w.end_time,
               w.role_on_shift, w.notes,
               t.train_id, t.name AS train_name
        FROM work_schedule w
        LEFT JOIN train t ON t.train_id = w.train_id
        JOIN employee e ON e.emp_id = w.emp_id
        WHERE w.emp_id = %s AND e.supervisor_id = %s
    """
    params = [emp_id, supervisor_scope_id]

    # Optional filters
    if date_from and date_to:
        sql += " AND w.shift_date BETWEEN %s AND %s"
        params += [date_from, date_to]
    elif date_from:
        sql += " AND w.shift_date >= %s"
        params.append(date_from)
    elif date_to:
        sql += " AND w.shift_date <= %s"
        params.append(date_to)

    sql += " ORDER BY w.shift_date, w.start_time"
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def create_schedule_scoped(emp_id: int, supervisor_scope_id: int, train_id: Optional[int],
                           shift_date: str, start_time: str, end_time: str,
                           role_on_shift: Optional[str], notes: Optional[str]):
    """Create schedule entry only for subordinate."""
    conn = get_connection()
    cur = conn.cursor()

    # verify scope
    cur.execute("SELECT 1 FROM employee WHERE emp_id=%s AND supervisor_id=%s",
                (emp_id, supervisor_scope_id))
    ok = cur.fetchone()
    if not ok:
        cur.close(); conn.close()
        raise PermissionError("Not allowed – employee not under this supervisor.")

    cur.execute("""
        INSERT INTO work_schedule (emp_id, train_id, shift_date, start_time, end_time, role_on_shift, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (emp_id, train_id, shift_date, start_time, end_time, role_on_shift, notes))

    conn.commit()
    cur.close(); conn.close()


def delete_schedule_scoped(shift_id: int, supervisor_scope_id: int):
    """Delete shift only if employee is subordinate."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE w FROM work_schedule w
        JOIN employee e ON e.emp_id = w.emp_id
        WHERE w.shift_id=%s AND e.supervisor_id=%s
    """, (shift_id, supervisor_scope_id))
    conn.commit()
    cur.close(); conn.close()


# ====================================================
# ✅ TRAIN STATUS (Supervisor can update any)
# ====================================================
def list_trains_with_status() -> List[Dict]:
    """Return trains with status + route details."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT t.train_id, t.name AS train_name, t.status,
               s1.station_name AS source, s2.station_name AS destination
        FROM train t
        LEFT JOIN route r ON t.route_id = r.route_id
        LEFT JOIN station s1 ON r.source_id = s1.station_id
        LEFT JOIN station s2 ON r.destination_id = s2.station_id
        ORDER BY t.train_id
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def update_train_status(train_id: int, status: str):
    """Update train status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE train SET status=%s WHERE train_id=%s", (status, train_id))
    conn.commit()
    cur.close(); conn.close()


# ====================================================
# ✅ BOOKINGS (Global View)
# ====================================================
def list_bookings_filtered(train_id: Optional[int], date_from: Optional[str],
                           date_to: Optional[str], query: str) -> List[Dict]:
    """Search + filter bookings."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
        SELECT b.booking_id, b.pnr, b.travel_date, b.seat_type, b.passenger_count, b.status,
               t.name AS train_name, p.first_name, p.last_name
        FROM booking b
        JOIN train t ON t.train_id = b.train_id
        JOIN passenger p ON p.passenger_id = b.passenger_id
        WHERE 1=1
    """
    params = []

    if train_id:
        sql += " AND b.train_id=%s"; params.append(train_id)

    if date_from and date_to:
        sql += " AND b.travel_date BETWEEN %s AND %s"; params += [date_from, date_to]
    elif date_from:
        sql += " AND b.travel_date >= %s"; params.append(date_from)
    elif date_to:
        sql += " AND b.travel_date <= %s"; params.append(date_to)

    if query:
        like = f"%{query}%"
        sql += " AND (p.first_name LIKE %s OR p.last_name LIKE %s OR b.pnr LIKE %s)"
        params += [like, like, like]

    sql += " ORDER BY b.travel_date DESC, b.booking_id DESC"
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


# ====================================================
# ✅ REPORTS (ScopED Inbox)
# ====================================================
def list_reports(status: str, supervisor_scope_id: int) -> List[Dict]:
    """List reports sent to supervisor."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT r.report_id, r.subject, r.status, r.created_at,
               e.first_name AS emp_first, e.last_name AS emp_last
        FROM supervisor_report r
        JOIN employee e ON e.emp_id = r.emp_id
        WHERE r.status=%s AND r.supervisor_id=%s
        ORDER BY r.created_at DESC
    """, (status, supervisor_scope_id))

    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_report_scoped(report_id: int, supervisor_scope_id: int) -> Optional[Dict]:
    """Fetch single report if belongs to supervisor."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT r.*, 
               e.first_name AS emp_first, e.last_name AS emp_last,
               s.first_name AS sup_first, s.last_name AS sup_last
        FROM supervisor_report r
        JOIN employee e ON e.emp_id = r.emp_id
        JOIN employee s ON s.emp_id = r.supervisor_id
        WHERE r.report_id=%s AND r.supervisor_id=%s
    """, (report_id, supervisor_scope_id))

    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def set_report_status_scoped(report_id: int, new_status: str, supervisor_scope_id: int):
    """Update report status within scoped inbox."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE supervisor_report
        SET status=%s
        WHERE report_id=%s AND supervisor_id=%s
    """, (new_status, report_id, supervisor_scope_id))

    conn.commit()
    cur.close(); conn.close()
