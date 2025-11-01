from flask import Blueprint, render_template

# ----------------------------------------------------
# Blueprint for main/public pages (non-authenticated)
# ----------------------------------------------------
main_bp = Blueprint("main", __name__)

# ----------------------------------------------------
# Home page → loads home.html
# ----------------------------------------------------
@main_bp.route("/")
def home():
    return render_template("home.html")
