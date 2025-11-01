from functools import wraps
from flask import session, redirect, url_for, flash

# ================================================================
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------------------
# ✔ Ensures a user is logged in before accessing a route.
# ✔ If not logged in → redirects to login page with a warning.
# Usage:
#     @login_required
#     def dashboard():
#         ...
# ================================================================
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Check if user session exists
        if not session.get("user_id"):
            flash("Login required", "warning")
            return redirect(url_for("auth.login"))
        
        # User logged in → Continue to original function
        return fn(*args, **kwargs)

    return wrapper


# ================================================================
# ROLE REQUIRED DECORATOR
# ---------------------------------------------------------------
# ✔ Ensures user has required role(s) before accessing a route.
# ✔ If logged out → redirect to login.
# ✔ If logged in but wrong role → redirect to home.
# Usage:
#     @role_required("ADMIN", "SUPERVISOR")
#     def admin_panel():
#         ...
# ================================================================
def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            # Must be logged in
            if not session.get("user_id"):
                flash("Login required", "warning")
                return redirect(url_for("auth.login"))

            # Check if user role is permitted
            role = session.get("role")
            if role not in allowed_roles:
                flash("Access denied", "danger")
                return redirect(url_for("main.home"))

            # Authorized → Run original function
            return fn(*args, **kwargs)

        return wrapper

    return decorator
