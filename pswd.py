"""
Password Hash Update Utility
----------------------------
Hashes and updates initial RMS passwords for:
✅ employee
✅ admin

Uses Werkzeug’s generate_password_hash().
"""

from werkzeug.security import generate_password_hash
from database.connection import get_connection


def set_hash_employee(email: str, plain: str):
    """
    Hash + update an employee password by email.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        hashed = generate_password_hash(plain)
        cur.execute(
            "UPDATE employee SET password=%s WHERE email=%s",
            (hashed, email)
        )
        conn.commit()

        cur.close()
        conn.close()

        print(f"✔ Employee updated → {email}")

    except Exception as e:
        print(f"❌ Employee update failed ({email}): {e}")


def set_hash_admin(email: str, plain: str):
    """
    Hash + update an admin password by email.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        hashed = generate_password_hash(plain)
        cur.execute(
            "UPDATE admin SET password=%s WHERE email=%s",
            (hashed, email)
        )
        conn.commit()

        cur.close()
        conn.close()

        print(f"✔ Admin updated → {email}")

    except Exception as e:
        print(f"❌ Admin update failed ({email}): {e}")


if __name__ == "__main__":

    # Preview example hashes
    print("emp123  →", generate_password_hash("emp123"))
    print("admin123 →", generate_password_hash("admin123"))
    print()

    # -----------------------------------------------------
    # Update Supervisor Passwords
    # -----------------------------------------------------
    set_hash_employee("sneha@rms.local",  "sneha123")
    set_hash_employee("sahana@rms.local", "sahana123")

    # -----------------------------------------------------
    # Update Employees under Sneha
    # -----------------------------------------------------
    set_hash_employee("ravi@rms.local",   "ravi123")
    set_hash_employee("arjun@rms.local",  "arjun123")
    set_hash_employee("kiran@rms.local",  "kiran123")
    set_hash_employee("kavya@rms.local",  "kavya123")

    # -----------------------------------------------------
    # Update Employees under Sahana
    # -----------------------------------------------------
    set_hash_employee("vijay@rms.local",  "vijay123")
    set_hash_employee("suresh@rms.local", "suresh123")
    set_hash_employee("priya@rms.local",  "priya123")
    set_hash_employee("krithi@rms.local", "krithi123")

    # -----------------------------------------------------
    # Update Admin
    # -----------------------------------------------------
    set_hash_admin("admin@rms.local", "admin123")

    print("\n✅ Password update complete.\n")
