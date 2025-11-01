"""
admin.py
--------
Admin module routes.

Admin capabilities:
✅ Dashboard
✅ Manage Trains      (Add / Edit / Delete)
✅ Manage Stations    (Add / Edit / Delete)
✅ Manage Routes      (Add / Edit / Delete)
✅ Manage Passengers  (Search / Activate / Delete)
✅ Manage Employees   (Create / Edit / Activate / Assign Supervisor)
✅ View Reports       (Revenue / Bookings / Employee Assignments)

NOTE:
• Full backend logic comes from services.admin_service
• All admin routes protected by @role_required("ADMIN")
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.decorators import role_required
from database.connection import get_connection
from mysql.connector import IntegrityError

# Load service layer functions (business logic)
from services.admin_service import (
    # Trains
    list_trains_with_route, get_train, create_train, update_train, delete_train,

    # Stations
    list_stations, get_station, create_station, update_station, delete_station,

    # Routes
    list_routes_full, get_route, create_route, update_route, delete_route,

    # Passengers
    list_passengers, delete_passenger, set_passenger_active,

    # Employees
    list_employees_all, get_employee, create_employee_admin, update_employee_admin, set_employee_active,

    # Reports
    revenue_report, bookings_report, assignment_report
)


# Blueprint config
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------
#  Admin Dashboard
# ---------------------------------------------------------------------
@admin_bp.route("/dashboard")
@role_required("ADMIN")
def dashboard():
    """
    Simple dashboard landing page.
    """
    return render_template("admin/dashboard.html")


# =====================================================================
#  TRAINS
# =====================================================================

@admin_bp.route("/trains")
@role_required("ADMIN")
def trains():
    """
    List all trains with route info.
    """
    rows = list_trains_with_route()
    return render_template("admin/trains.html", rows=rows)


@admin_bp.route("/trains/create", methods=["GET", "POST"])
@role_required("ADMIN")
def train_create():
    """
    Create a train with route + status.
    """
    if request.method == "POST":
        name = request.form.get("name")
        route_id = int(request.form.get("route_id"))
        status = request.form.get("status") or "ON-TIME"

        try:
            create_train(name, route_id, status)
            flash("Train created.", "success")
            return redirect(url_for("admin.trains"))
        except Exception as e:
            flash(str(e), "danger")

    routes = list_routes_full()
    return render_template("admin/train_create.html", routes=routes)


@admin_bp.route("/trains/edit/<int:train_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def train_edit(train_id: int):
    """
    Edit train details.
    """
    t = get_train(train_id)
    if not t:
        flash("Train not found.", "warning")
        return redirect(url_for("admin.trains"))

    if request.method == "POST":
        name = request.form.get("name")
        route_id = int(request.form.get("route_id"))
        status = request.form.get("status")

        update_train(train_id, name, route_id, status)
        flash("Train updated.", "success")
        return redirect(url_for("admin.trains"))

    routes = list_routes_full()
    return render_template("admin/train_edit.html", t=t, routes=routes)


@admin_bp.route("/trains/delete/<int:train_id>", methods=["POST"])
@role_required("ADMIN")
def train_delete(train_id):
    train_id = request.form.get("train_id")

    conn = get_connection()
    cur = conn.cursor()

    message_error = None
    message_success = None

    try:
        cur.execute("DELETE FROM train WHERE train_id=%s", (train_id,))
        conn.commit()

        if cur.rowcount > 0:
            message_success = "Train deleted successfully!"
        else:
            message_error = "⚠ Train not found."
    except IntegrityError:
        # FK failure – referenced in route/booking/schedule
        message_error = (
            "⚠ Cannot delete: train still referenced (Route / Booking / Schedule). "
            "Remove dependencies first."
        )
        conn.rollback()
    except Exception as e:
        message_error = f"⚠ Error: {str(e)}"
        conn.rollback()

    cur.close()
    conn.close()

    # Reload updated train list
    rows = list_trains_with_route()

    return render_template(
        "admin/trains.html",
        rows=rows,
        error=message_error,
        success=message_success,
    )




# =====================================================================
#  STATIONS
# =====================================================================

@admin_bp.route("/stations")
@role_required("ADMIN")
def stations():
    """
    List stations
    """
    rows = list_stations()
    return render_template("admin/stations.html", rows=rows)


@admin_bp.route("/stations/create", methods=["GET", "POST"])
@role_required("ADMIN")
def station_create():
    """
    Add station
    """
    if request.method == "POST":
        name = request.form.get("station_name")

        try:
            create_station(name)
            flash("Station created.", "success")
            return redirect(url_for("admin.stations"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("admin/station_create.html")


@admin_bp.route("/stations/edit/<int:station_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def station_edit(station_id: int):
    """
    Edit station name.
    """
    s = get_station(station_id)
    if not s:
        flash("Station not found.", "warning")
        return redirect(url_for("admin.stations"))

    if request.method == "POST":
        name = request.form.get("station_name")
        update_station(station_id, name)
        flash("Station updated.", "success")
        return redirect(url_for("admin.stations"))

    return render_template("admin/station_edit.html", s=s)


@admin_bp.route("/stations/delete", methods=["POST"])
@role_required("ADMIN")
def station_delete():
    """
    Delete station safely, returning message if blocked.
    """
    station_id = int(request.form.get("station_id"))

    success, message = delete_station(station_id)
    flash(message, "success" if success else "danger")

    return redirect(url_for("admin.stations"))


# =====================================================================
#  ROUTES
# =====================================================================

@admin_bp.route("/routes")
@role_required("ADMIN")
def routes():
    """
    List routes with full station info.
    """
    rows = list_routes_full()
    stations = list_stations()
    return render_template("admin/routes.html", rows=rows, stations=stations)


@admin_bp.route("/routes/create", methods=["GET", "POST"])
@role_required("ADMIN")
def route_create():
    """
    Add route.
    """
    if request.method == "POST":
        source_id = int(request.form.get("source_id"))
        destination_id = int(request.form.get("destination_id"))
        distance_km = float(request.form.get("distance_km"))
        duration = request.form.get("duration")

        create_route(source_id, destination_id, distance_km, duration)
        flash("Route created.", "success")
        return redirect(url_for("admin.routes"))

    stations = list_stations()
    return render_template("admin/route_create.html", stations=stations)


@admin_bp.route("/routes/edit/<int:route_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def route_edit(route_id: int):
    """
    Edit route.
    """
    r = get_route(route_id)
    if not r:
        flash("Route not found.", "warning")
        return redirect(url_for("admin.routes"))

    if request.method == "POST":
        source_id = int(request.form.get("source_id"))
        destination_id = int(request.form.get("destination_id"))
        distance_km = float(request.form.get("distance_km"))
        duration = request.form.get("duration")

        update_route(route_id, source_id, destination_id, distance_km, duration)
        flash("Route updated.", "success")
        return redirect(url_for("admin.routes"))

    stations = list_stations()
    return render_template("admin/route_edit.html", r=r, stations=stations)


@admin_bp.route("/routes/delete", methods=["POST"])
@role_required("ADMIN")
def route_delete():
    route_id = request.form.get("route_id")
    if not route_id:
        flash("Invalid route.", "danger")
        return redirect(url_for("admin.routes"))

    try:
        delete_route(route_id)
        flash("Route deleted successfully.", "success")

    except IntegrityError:
        flash(
            "⚠ Cannot delete: Route is referenced by one or more Trains. "
            "Delete/modify related Trains first.",
            "danger"
        )

    except Exception as e:
        flash(f"⚠ Error: {str(e)}", "danger")

    return redirect(url_for("admin.routes"))



# =====================================================================
#  PASSENGERS
# =====================================================================

@admin_bp.route("/passengers")
@role_required("ADMIN")
def passengers():
    """
    List + search passengers.
    """
    q = (request.args.get("q") or "").strip()
    rows = list_passengers(q)
    return render_template("admin/passengers.html", rows=rows, q=q)


@admin_bp.route("/passengers/delete", methods=["POST"])
@role_required("ADMIN")
def passenger_delete():
    pid = request.form.get("passenger_id")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM passenger WHERE passenger_id=%s", (pid,))
        conn.commit()

        flash("Passenger deleted successfully.", "success")

    except Exception as e:
        msg = str(e)

        # Foreign key constraint failure
        if "1451" in msg or "foreign key constraint fails" in msg.lower():
            flash("❌Cannot delete passenger — bookings exist under this passenger.", "danger")
        else:
            flash(f"❌Failed to delete passenger: {msg}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin.passengers"))



@admin_bp.route("/passengers/toggle", methods=["POST"])
@role_required("ADMIN")
def passenger_toggle():
    """
    Toggle passenger active/inactive.
    """
    pid = int(request.form.get("passenger_id"))
    active = int(request.form.get("active"))

    try:
        set_passenger_active(pid, active)
        flash("Passenger status updated.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("admin.passengers"))


# =====================================================================
#  EMPLOYEES
# =====================================================================
@admin_bp.route("/employees")
@role_required("ADMIN")
def employees():
    """
    Admin view → list all employees
    """

    q = request.args.get("q", "").strip()

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if q:
        cur.execute(
            """
            SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id
            FROM employee
            WHERE first_name LIKE %s
               OR last_name LIKE %s
               OR email LIKE %s
            ORDER BY emp_id
            """,
            (f"%{q}%", f"%{q}%", f"%{q}%"),
        )
    else:
        cur.execute(
            """
            SELECT emp_id, first_name, last_name, email, role, salary, supervisor_id
            FROM employee
            ORDER BY emp_id
            """
        )

    rows = cur.fetchall()

    # Build supervisor lookup map
    cur.execute(
        "SELECT emp_id, first_name, last_name FROM employee WHERE role='SUPERVISOR'"
    )
    sups = cur.fetchall()

    supervisors_map = {
        s["emp_id"]: f"{s['first_name']} {s['last_name']}"
        for s in sups
    }

    cur.close()
    conn.close()

    # Pass supervisors_map to template
    return render_template(
        "admin/employees.html",
        rows=rows,
        q=q,
        supervisors_map=supervisors_map,
    )



@admin_bp.route("/employees/create", methods=["GET", "POST"])
@role_required("ADMIN")
def employee_create():
    """
    Create new employee
    Supervisor is optional
    """
    if request.method == "POST":
        first = request.form.get("first_name")
        last  = request.form.get("last_name")
        email = request.form.get("email")
        role  = request.form.get("role")
        salary = float(request.form.get("salary") or 0)

        supervisor_id = request.form.get("supervisor_id")
        supervisor_id = int(supervisor_id) if supervisor_id else None

        try:
            create_employee_admin(first, last, email, role, salary, supervisor_id)
            flash("Employee created.", "success")
            return redirect(url_for("admin.employees"))
        except Exception as e:
            flash(str(e), "danger")

    sups = list_employees_all(role_filter="SUPERVISOR")
    return render_template("admin/employee_create.html", supervisors=sups)


@admin_bp.route("/employees/edit/<int:emp_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def employee_edit(emp_id: int):
    """
    Modify employee details
    """
    emp = get_employee(emp_id)
    if not emp:
        flash("Employee not found.", "warning")
        return redirect(url_for("admin.employees"))

    if request.method == "POST":
        role = request.form.get("role")
        salary = float(request.form.get("salary") or 0)

        supervisor_id = request.form.get("supervisor_id")
        supervisor_id = int(supervisor_id) if supervisor_id else None

        active = 1 if request.form.get("active") == "on" else 0

        try:
            set_employee_active(emp_id, active)
            update_employee_admin(emp_id, role, salary, supervisor_id)
            flash("Employee updated.", "success")
            return redirect(url_for("admin.employees"))
        except Exception as e:
            flash(str(e), "danger")

    sups = list_employees_all(role_filter="SUPERVISOR")
    return render_template("admin/employee_edit.html", emp=emp, supervisors=sups)


# =====================================================================
#  REPORTS
# =====================================================================

@admin_bp.route("/reports")
@role_required("ADMIN")
def reports_home():
    """
    Main reports hub
    """
    return render_template("admin/reports.html")


@admin_bp.route("/reports/revenue")
@role_required("ADMIN")
def reports_revenue():
    """
    Revenue report, filtered by:
      • Date range
      • Train
    """
    date_from = request.args.get("from")
    date_to   = request.args.get("to")
    train_id  = request.args.get("train_id", type=int)

    rows, total = revenue_report(date_from, date_to, train_id)
    trains = list_trains_with_route()

    return render_template(
        "admin/report_revenue.html",
        rows=rows,
        total=total,
        date_from=date_from or "",
        date_to=date_to or "",
        trains=trains,
        sel_train=train_id
    )


@admin_bp.route("/reports/bookings")
@role_required("ADMIN")
def reports_bookings():
    """
    Booking report, filtered by:
      • Date range
      • Train
    """
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    train_id = request.args.get("train_id", type=int)

    rows = bookings_report(date_from, date_to, train_id)
    trains = list_trains_with_route()

    return render_template(
        "admin/report_bookings.html",
        rows=rows,
        date_from=date_from or "",
        date_to=date_to or "",
        trains=trains,
        sel_train=train_id
    )


@admin_bp.route("/reports/assignments")
@role_required("ADMIN")
def reports_assignments():
    """
    Employee → train assignment report
    """
    rows = assignment_report()
    return render_template("admin/report_assignments.html", rows=rows)
