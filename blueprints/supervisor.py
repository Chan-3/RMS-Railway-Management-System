from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import role_required
from services.supervisor_service import (
    ALLOWED_STAFF_ROLES,
    # employees
    list_employees, get_employee_scoped, create_employee_under_supervisor,
    update_employee_core_scoped,
    # assignments
    list_trains_basic, list_assignments_for_emp, assign_emp_to_train_scoped, remove_assignment_scoped,
    # schedules
    list_schedule_for_employee, create_schedule_scoped, delete_schedule_scoped,
    # status
    list_trains_with_status, update_train_status,
    # bookings
    list_bookings_filtered,
    # reports
    list_reports, get_report_scoped, set_report_status_scoped,
)

# ----------------------------------------------------
# Supervisor Blueprint
# ----------------------------------------------------
supervisor_bp = Blueprint("supervisor", __name__, url_prefix="/supervisor")


# ----------------------------------------------------
# Dashboard
# ----------------------------------------------------
@supervisor_bp.route("/dashboard")
@role_required("SUPERVISOR")
def dashboard():
    return render_template("supervisor/dashboard.html")


# ====================================================
# ✅ EMPLOYEES (SCOPED)
# ====================================================
@supervisor_bp.route("/employees")
@role_required("SUPERVISOR")
def employees_list():
    """List employees under this supervisor"""
    sup_id = session.get("user_id")
    q = (request.args.get("q") or "").strip()
    rows = list_employees(q=q, supervisor_scope_id=sup_id)
    return render_template("supervisor/employees_list.html", rows=rows, q=q)


@supervisor_bp.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
@role_required("SUPERVISOR")
def employee_edit(emp_id: int):
    """Edit employee role + salary (within supervisor scope)"""
    sup_id = session.get("user_id")
    emp = get_employee_scoped(emp_id, sup_id)

    if not emp:
        flash("Not found or not in your team.", "warning")
        return redirect(url_for("supervisor.employees_list"))

    if request.method == "POST":
        role = request.form.get("role")
        salary = float(request.form.get("salary") or 0)
        try:
            ok = update_employee_core_scoped(emp_id, sup_id, role, salary)
            flash(
                "Employee updated." if ok else "No change or not permitted.",
                "success" if ok else "warning"
            )
            return redirect(url_for("supervisor.employees_list"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("supervisor/employee_edit.html", emp=emp, roles=ALLOWED_STAFF_ROLES)


# ====================================================
# ✅ ASSIGNMENTS (SCOPED)
# ====================================================
@supervisor_bp.route("/assignments", methods=["GET", "POST"])
@role_required("SUPERVISOR")
def assignments():
    """Assign employees to trains"""
    sup_id = session.get("user_id")
    emp_id = request.args.get("emp_id", type=int)

    employees = list_employees(supervisor_scope_id=sup_id)
    trains = list_trains_basic()
    rows = list_assignments_for_emp(emp_id, sup_id) if emp_id else []

    if request.method == "POST":
        emp_id = int(request.form.get("emp_id"))
        train_id = int(request.form.get("train_id"))
        try:
            assign_emp_to_train_scoped(emp_id, train_id, sup_id)
            flash("Assignment saved.", "success")
        except Exception as e:
            flash(str(e), "danger")
        return redirect(url_for("supervisor.assignments", emp_id=emp_id))

    return render_template(
        "supervisor/assignments.html",
        employees=employees, trains_tr=trains,
        rows=rows, sel_emp_id=emp_id
    )


@supervisor_bp.route("/assignments/remove", methods=["POST"])
@role_required("SUPERVISOR")
def assignments_remove():
    """Remove employee → train assignment"""
    sup_id = session.get("user_id")
    emp_id = int(request.form.get("emp_id"))
    train_id = int(request.form.get("train_id"))
    try:
        remove_assignment_scoped(emp_id, train_id, sup_id)
        flash("Assignment removed.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("supervisor.assignments", emp_id=emp_id))


# ====================================================
# ✅ SCHEDULE (SCOPED)
# ====================================================
@supervisor_bp.route("/schedule", methods=["GET", "POST"])
@role_required("SUPERVISOR")
def schedule_manage():
    """Create + list work schedules scoped by supervisor"""
    sup_id = session.get("user_id")

    emp_id = request.args.get("emp_id", type=int)
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    employees = list_employees(supervisor_scope_id=sup_id)
    trains = list_trains_basic()

    rows = list_schedule_for_employee(emp_id, sup_id, date_from, date_to) if emp_id else []

    # Create schedule
    if request.method == "POST":
        emp_id_p = int(request.form.get("emp_id"))
        train_id = request.form.get("train_id")
        train_id = int(train_id) if train_id else None

        shift_date = request.form.get("shift_date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        role_on = request.form.get("role_on_shift")
        notes = request.form.get("notes")

        try:
            create_schedule_scoped(
                emp_id_p, sup_id, train_id,
                shift_date, start_time, end_time,
                role_on, notes
            )
            flash("Shift created.", "success")
        except Exception as e:
            flash(str(e), "danger")

        return redirect(url_for("supervisor.schedule_manage", emp_id=emp_id_p))

    return render_template(
        "supervisor/schedule_manage.html",
        employees=employees, trains=trains, rows=rows,
        sel_emp_id=emp_id,
        date_from=date_from or "", date_to=date_to or ""
    )


@supervisor_bp.route("/schedule/delete", methods=["POST"])
@role_required("SUPERVISOR")
def schedule_delete():
    """Delete a scheduled shift"""
    sup_id = session.get("user_id")
    sid = int(request.form.get("shift_id"))
    emp_id = int(request.form.get("emp_id"))

    delete_schedule_scoped(sid, sup_id)
    flash("Shift deleted.", "success")

    return redirect(url_for("supervisor.schedule_manage", emp_id=emp_id))


# ====================================================
# ✅ TRAIN STATUS (GLOBAL)
# ====================================================
@supervisor_bp.route("/status", methods=["GET", "POST"])
@role_required("SUPERVISOR")
def status_manage():
    """Supervisor can update train operational status"""
    if request.method == "POST":
        train_id = int(request.form.get("train_id"))
        status = request.form.get("status")
        update_train_status(train_id, status)
        flash("Status updated.", "success")

    rows = list_trains_with_status()
    return render_template("supervisor/train_status_manage.html", rows=rows)


# ====================================================
# ✅ BOOKINGS (GLOBAL VIEW)
# ====================================================
@supervisor_bp.route("/bookings")
@role_required("SUPERVISOR")
def bookings():
    """Search + filter global bookings"""
    train_id = request.args.get("train_id", type=int)
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    q = (request.args.get("q") or "").strip()

    trains = list_trains_basic()
    rows = list_bookings_filtered(train_id, date_from, date_to, q)

    return render_template(
        "supervisor/bookings.html",
        rows=rows, trains=trains,
        sel_train=train_id,
        date_from=date_from or "", date_to=date_to or "",
        q=q
    )


# ====================================================
# ✅ REPORTS (SCOPED)
# ====================================================
@supervisor_bp.route("/reports")
@role_required("SUPERVISOR")
def reports_inbox():
    """Reports sent to this supervisor"""
    sup_id = session.get("user_id")
    status = request.args.get("status") or "NEW"

    rows = list_reports(status, sup_id)
    return render_template("supervisor/reports_inbox.html", rows=rows, status=status)


@supervisor_bp.route("/reports/<int:report_id>")
@role_required("SUPERVISOR")
def report_view(report_id: int):
    """View single report"""
    sup_id = session.get("user_id")
    r = get_report_scoped(report_id, sup_id)
    if not r:
        flash("Report not found or not in your inbox.", "warning")
        return redirect(url_for("supervisor.reports_inbox"))
    return render_template("supervisor/report_view.html", r=r)


@supervisor_bp.route("/reports/<int:report_id>/set", methods=["POST"])
@role_required("SUPERVISOR")
def report_set_status(report_id: int):
    """Update supervisor report status"""
    sup_id = session.get("user_id")
    new_status = request.form.get("status")

    set_report_status_scoped(report_id, new_status, sup_id)
    flash("Report status updated.", "success")

    return redirect(url_for("supervisor.report_view", report_id=report_id))
