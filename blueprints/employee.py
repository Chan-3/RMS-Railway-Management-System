"""
EMPLOYEE BLUEPRINT
Handles employee-side dashboard, trains, bookings, schedule,
assignments, and supervisor reporting.
"""

from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from utils.decorators import role_required
from database.connection import get_connection
from services.employee_service import (
    get_employee_profile,
    list_all_trains_with_route,
    list_trains_basic,
    list_bookings_for_train,
    get_train_seat_capacity,
    upsert_train_seat_capacity,
    update_train_status,
    list_assignments_for_employee,
    list_schedule_for_employee,
    create_report_to_supervisor,
    list_my_reports
)

# Blueprint → /employee/...
employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


# ====================================================
# ✅ Dashboard
# ====================================================
@employee_bp.route("/dashboard")
@role_required("EMPLOYEE")
def dashboard():
    """
    Simple employee home page.
    """
    return render_template("employee/dashboard.html")


# ====================================================
# ✅ My Profile
# ====================================================
@employee_bp.route("/profile")
@role_required("EMPLOYEE")
def profile():
    """
    Displays employee details.
    """
    emp_id = session.get("user_id")
    emp = get_employee_profile(emp_id)
    return render_template("employee/profile.html", emp=emp)


# ====================================================
# ✅ Trains — View / Manage
# ====================================================
@employee_bp.route("/trains")
@role_required("EMPLOYEE")
def trains():
    """
    Shows list of trains + route details.
    """
    rows = list_all_trains_with_route()
    return render_template("employee/trains.html", trains=rows)


# ====================================================
# ✅ Update Train (status + seat capacity)
# ====================================================
@employee_bp.route("/trains/update/<int:train_id>", methods=["GET", "POST"])
@role_required("EMPLOYEE")
def update_train(train_id: int):
    """
    GET  → show seat + status update form
    POST → update seat capacity + train status
    """
    # --- POST: update database
    if request.method == "POST":
        general = int(request.form.get("GENERAL") or 0)
        sleeper = int(request.form.get("SLEEPER") or 0)
        ac      = int(request.form.get("AC") or 0)

        # Update seats
        upsert_train_seat_capacity(train_id, "GENERAL", general)
        upsert_train_seat_capacity(train_id, "SLEEPER", sleeper)
        upsert_train_seat_capacity(train_id, "AC", ac)

        # Update status
        new_status = request.form.get("status")
        update_train_status(train_id, new_status)

        flash("Train details updated successfully.", "success")
        return redirect(url_for("employee.trains"))

    # --- GET: fetch train + seats
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.train_id, t.name AS train_name, t.status,
               s1.station_name AS source, 
               s2.station_name AS destination
        FROM train t 
        LEFT JOIN route r ON t.route_id = r.route_id
        LEFT JOIN station s1 ON r.source_id = s1.station_id
        LEFT JOIN station s2 ON r.destination_id = s2.station_id
        WHERE t.train_id = %s
    """, (train_id,))
    train = cur.fetchone()

    cur.close()
    conn.close()

    seats = get_train_seat_capacity(train_id)

    return render_template("employee/update_train.html", train=train, seats=seats)


# ====================================================
# ✅ Bookings — Select Train
# ====================================================
@employee_bp.route("/bookings")
@role_required("EMPLOYEE")
def bookings_trains():
    """
    Page to choose train before viewing bookings.
    """
    trains = list_trains_basic()
    return render_template("employee/bookings_trains.html", trains=trains)


# ====================================================
# ✅ Bookings for specific train
# ====================================================
@employee_bp.route("/bookings/<int:train_id>")
@role_required("EMPLOYEE")
def bookings_for_train(train_id: int):
    """
    Shows list of bookings for a train.
    """
    rows = list_bookings_for_train(train_id)
    return render_template("employee/bookings_list.html", bookings=rows, train_id=train_id)


# ====================================================
# ✅ My Train Assignments
# ====================================================
@employee_bp.route("/assignments", endpoint="assignments")
@role_required("EMPLOYEE")
def my_assignments():
    """
    Shows trains assigned to this employee.
    """
    emp_id = session.get("user_id")
    rows = list_assignments_for_employee(emp_id)
    return render_template("employee/assignments.html", rows=rows)


# ====================================================
# ✅ Work Schedule (optional date filter)
# ====================================================
@employee_bp.route("/schedule")
@role_required("EMPLOYEE")
def my_schedule():
    """
    Shows employee work schedule, with optional date filtering.
    """
    emp_id = session.get("user_id")
    date_from = request.args.get("from")  # YYYY-MM-DD
    date_to   = request.args.get("to")    # YYYY-MM-DD
    rows = list_schedule_for_employee(emp_id, date_from, date_to)

    return render_template(
        "employee/schedule.html",
        rows=rows,
        date_from=date_from or "",
        date_to=date_to or ""
    )


# ====================================================
# ✅ Report to Supervisor
# ====================================================
@employee_bp.route("/report", methods=["GET", "POST"])
@role_required("EMPLOYEE")
def report_supervisor():
    """
    GET  → display report form
    POST → store new report
    """
    if request.method == "POST":

        emp_id  = session.get("user_id")
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not subject or not message:
            flash("Subject and message are required.", "warning")
            return redirect(url_for("employee.report_supervisor"))

        try:
            rid = create_report_to_supervisor(emp_id, subject, message)
            flash(f"Report submitted (ID: {rid}).", "success")
        except ValueError as ex:
            flash(str(ex), "danger")

        return redirect(url_for("employee.my_reports"))

    return render_template("employee/report_form.html")


# ====================================================
# ✅ View My Reports
# ====================================================
@employee_bp.route("/reports")
@role_required("EMPLOYEE")
def my_reports():
    """
    Shows all reports submitted by employee.
    """
    emp_id = session.get("user_id")
    rows = list_my_reports(emp_id)
    return render_template("employee/reports.html", rows=rows)
