"""
auth.py
---------
Handles Login / Register / Logout routes.
Uses service functions from `auth_service.py`.
"""

from flask import Blueprint
from services.auth_service import register_user, login_user, logout_user

# ✅ Blueprint for authentication
# All auth routes will start with "/auth"
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    ✅ Login route
    GET  → show login form
    POST → process login attempt
    
    Delegates logic to `login_user(request)`
    """
    from flask import request
    return login_user(request)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    ✅ Registration route
    GET  → show register form
    POST → create new user
    
    Delegates logic to `register_user(request)`
    """
    from flask import request
    return register_user(request)


@auth_bp.route("/logout")
def logout():
    """
    ✅ Logout route
    Clears session and redirects to home/login
    
    Delegates to logout_user()
    """
    return logout_user()
