"""
app.py
------
Main Flask application factory.

✔ Registers all Blueprints
✔ Injects user role + user_id into templates
✔ Uses SECRET_KEY from config
"""

from flask import Flask, session
from config import SECRET_KEY

# Blueprints
from blueprints.main import main_bp
from blueprints.auth import auth_bp
from blueprints.passenger import passenger_bp
from blueprints.employee import employee_bp
from blueprints.supervisor import supervisor_bp
from blueprints.admin import admin_bp


def create_app():
    """
    Application factory:
      - Creates Flask app
      - Sets secret key
      - Registers blueprints
      - Provides global template variables
    """
    app = Flask(__name__)
    app.secret_key = SECRET_KEY   # session encryption

    # -------------------------------------------------------
    # Make user role + id available in ALL templates
    # -------------------------------------------------------
    @app.context_processor
    def inject_role():
        return {
            "current_role": session.get("role"),
            "current_user_id": session.get("user_id"),
        }

    # -------------------------------------------------------
    # BLUEPRINT REGISTRATION
    # -------------------------------------------------------
    app.register_blueprint(main_bp)        # Home
    app.register_blueprint(auth_bp)        # Login, register
    app.register_blueprint(passenger_bp)   # Passenger module
    app.register_blueprint(employee_bp)    # Employee module
    app.register_blueprint(supervisor_bp)  # Supervisor module
    app.register_blueprint(admin_bp)       # Admin module

    return app


# -------------------------------------------------------
# Run Server
# -------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)   # development mode
