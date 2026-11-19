"""
Seed default data into the database.
- Default admin user (password hashed with bcrypt)
- Blood inventory rows for all 8 blood groups
"""

import bcrypt
from database.connection import get_connection
from config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
from utils.constants import BLOOD_GROUPS


def seed_default_data():
    """Insert default admin and blood inventory if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ─── Seed Admin User ─────────────────────────────────────
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = ?",
            (DEFAULT_ADMIN_USERNAME,)
        )
        if cursor.fetchone()[0] == 0:
            password_hash = bcrypt.hashpw(
                DEFAULT_ADMIN_PASSWORD.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (DEFAULT_ADMIN_USERNAME, password_hash, "admin")
            )

        # ─── Seed Blood Inventory ────────────────────────────────
        for blood_group in BLOOD_GROUPS:
            cursor.execute(
                "SELECT COUNT(*) FROM blood_inventory WHERE blood_group = ?",
                (blood_group,)
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO blood_inventory (blood_group, units_available) VALUES (?, ?)",
                    (blood_group, 0)
                )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
