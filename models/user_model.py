"""
User model — data access layer for the users table.
All queries use parameterized statements to prevent SQL injection.
"""

from database.connection import get_connection


def get_user_by_username(username):
    """Fetch a user by username. Returns dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def create_user(username, password_hash, role="Staff Member"):
    """Create a new user. Returns the new user ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def update_password(username, new_password_hash):
    """Update a user's password hash. Returns True on success."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_password_hash, username),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_all_users():
    """Fetch all users (excluding password hashes)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
