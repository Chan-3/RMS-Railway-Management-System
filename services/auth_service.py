"""
auth_service.py
----------------
Handles authentication logic:
- Registration (Passenger only)
- Login (Passenger, Employee, Supervisor, Admin)
- Logout
Stores role + user_id in session

NOTE:
• Supervisor is detected when employee.supervisor_id IS NULL
"""

from flask import render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_connection


# =====================================================================
#  Helper — Query Passenger
# =====================================================================
def _find_passenger(email: str):
    """
    Returns passenger row if found:
    {
        user_id,
        email,
        password,
        role="PASSENGER"
    }
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT passenger_id AS user_id, email, password
        FROM passenger
        WHERE email=%s
    """, (email,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    # Label role if exists
    if row:
        row["role"] = "PASSENGER"
    return row


# =====================================================================
#  Helper — Query Employee → (EMPLOYEE / SUPERVISOR)
# =====================================================================
def _find_employee(email: str):
    """
    Returns employee row:
    {
        user_id,
        email,
        password,
        supervisor_id,
        role="SUPERVISOR" if no supervisor else "EMPLOYEE"
    }
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT emp_id AS user_id, email, password, supervisor_id
        FROM employee
        WHERE email=%s
    """, (email,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        # Supervisor → no supervisor assigned
        row["role"] = "SUPERVISOR" if row["supervisor_id"] is None else "EMPLOYEE"
    return row


# =====================================================================
#  Helper — Query Admin
# =====================================================================
def _find_admin(email: str):
    """
    Returns admin row:
    {
        user_id,
        email,
        password,
        role="ADMIN"
    }
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT admin_id AS user_id, email, password
        FROM admin
        WHERE email=%s
    """, (email,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        row["role"] = "ADMIN"
    return row


# =====================================================================
#  Helper — Set session
# =====================================================================
def _set_session(user_id, role):
    """
    Stores logged-in user_id + role in Flask session
    """
    session["user_id"] = user_id
    session["role"] = role


# =====================================================================
#  Helper — Send user to appropriate dashboard
# =====================================================================
def _role_home(role: str) -> str:
    """
    Maps role → Landing route
    """
    return {
        "PASSENGER": "/passenger/dashboard",
        "EMPLOYEE": "/employee/dashboard",
        "SUPERVISOR": "/supervisor/dashboard",
        "ADMIN": "/admin/dashboard",
    }.get(role, "/")


# =====================================================================
#  REGISTER (PASSENGER ONLY)
# =====================================================================
def register_user(req):
    """
    Handles passenger registration.

    GET  → return register page
    POST → write passenger to DB
    """
    if req.method == "POST":

        fn = req.form.get("first_name")
        ln = req.form.get("last_name")
        email = req.form.get("email")
        phone = req.form.get("phone")
        gender = req.form.get("gender")
        age = req.form.get("age")
        raw_pass = req.form.get("password")

        # Basic check
        if not all([fn, ln, email, phone, gender, age, raw_pass]):
            flash("All fields are required", "danger")
            return render_template("auth/register.html")

        hashed = generate_password_hash(raw_pass)

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO passenger(first_name,last_name,email,phone,gender,age,password)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (fn, ln, email, phone, gender, age, hashed))

            conn.commit()

        except Exception as e:
            conn.rollback()
            flash(f"Registration failed: {e}", "danger")
            cur.close()
            conn.close()
            return render_template("auth/register.html")

        cur.close()
        conn.close()

        flash("Registered successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    # GET
    return render_template("auth/register.html")


# =====================================================================
#  LOGIN (ALL ROLES)
# =====================================================================
def login_user(req):
    """
    Handles login for:
    • PASSENGER
    • EMPLOYEE
    • SUPERVISOR
    • ADMIN

    Flow:
      1) Try passenger
      2) Try employee/supervisor
      3) Try admin
    """
    if req.method == "POST":

        email = req.form.get("email")
        raw = req.form.get("password")

        if not email or not raw:
            return render_template("auth/login.html", error="Email and password required")

        # Try passenger
        u = _find_passenger(email)
        if u and check_password_hash(u["password"], raw):
            _set_session(u["user_id"], u["role"])
            return redirect(_role_home(u["role"]))

        # Try employee / supervisor
        u = _find_employee(email)
        if u and check_password_hash(u["password"], raw):
            _set_session(u["user_id"], u["role"])
            return redirect(_role_home(u["role"]))

        # Try admin
        u = _find_admin(email)
        if u and check_password_hash(u["password"], raw):
            _set_session(u["user_id"], u["role"])
            return redirect(_role_home(u["role"]))

        # All failed
        return render_template("auth/login.html", error="Wrong credentials")

    # GET
    return render_template("auth/login.html")


# =====================================================================
#  LOGOUT
# =====================================================================
def logout_user():
    """
    Clears session and redirects to home
    """
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("main.home"))
