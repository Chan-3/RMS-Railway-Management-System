from flask import Blueprint, render_template, request, session
from utils.decorators import role_required
from services.search_service import search_trains
from services.booking_service import create_booking, cancel_booking
from services.history_service import get_history
from database.connection import get_connection
from flask import flash


# Passenger routes blueprint
passenger_bp = Blueprint("passenger", __name__, url_prefix="/passenger")


# -------------------------
# Dashboard
# -------------------------
@passenger_bp.route("/dashboard")
@role_required("PASSENGER")
def dashboard():
    return render_template("passenger/dashboard.html")

# -------------------------
# My Profile
# -------------------------
@passenger_bp.route("/profile", methods=["GET", "POST"])
@role_required("PASSENGER")
def profile():
    from database.connection import get_connection

    passenger_id = session.get("user_id")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        age = request.form.get("age", "")

        cur.execute("""
            UPDATE passenger 
            SET phone=%s, gender=%s, age=%s
            WHERE passenger_id=%s
        """, (phone, gender, age, passenger_id))

        conn.commit()
        flash("Profile updated successfully!", "success")   # MESSAGE

    cur.execute("SELECT * FROM passenger WHERE passenger_id=%s", (passenger_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("passenger/profile.html", p=row)



# -------------------------
# Book Tickets
# -------------------------
@passenger_bp.route("/book", methods=["GET", "POST"])
@role_required("PASSENGER")
def book():
    if request.method == "POST":
        data = {
            "train_id": request.form["train_id"],
            "route_id": request.form["route_id"],
            "travel_date": request.form["travel_date"],
            "seat_type": request.form["seat_type"],
            "count": request.form["count"],
            "payment_mode": request.form["payment_mode"],
        }
        result = create_booking(session["user_id"], data)
        return render_template("passenger/book.html", result=result)

    # Initial form view
    return render_template("passenger/book.html", result=None)


# -------------------------
# Cancel Booking
# -------------------------
@passenger_bp.route("/cancel", methods=["GET", "POST"])
@role_required("PASSENGER")
def cancel():
    result = None
    if request.method == "POST":
        bid = request.form["booking_id"]
        result = cancel_booking(bid)
    return render_template("passenger/cancel.html", result=result)


# -------------------------
# Booking History
# -------------------------
@passenger_bp.route("/history")
@role_required("PASSENGER")
def history():
    rows = get_history(session["user_id"])
    return render_template("passenger/history.html", rows=rows)


# -------------------------
# Search trains
# -------------------------
@passenger_bp.route("/search", methods=["GET"])
@role_required("PASSENGER")
def search():
    src = request.args.get("source", "").strip()
    dst = request.args.get("destination", "").strip()

    # Load station list
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT station_name FROM station")
    stations = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()

    trains = None
    message = None

    # No input → show empty form
    if not src and not dst:
        return render_template(
            "passenger/search.html",
            stations=stations,
            trains=None,
            message=None,
            source="",
            destination=""
        )

    # Same station → invalid
    if src == dst:
        message = "⚠ Source and Destination cannot be the same."
        return render_template(
            "passenger/search.html",
            stations=stations,
            trains=None,
            message=message,
            source=src,
            destination=dst
        )

    # Search trains
    trains = search_trains(src, dst)
    if not trains:
        message = f"⚠ No trains found between {src} and {dst}."

    return render_template(
        "passenger/search.html",
        stations=stations,
        trains=trains,
        message=message,
        source=src,
        destination=dst
    )
