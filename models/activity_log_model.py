"""
Activity log model — records important actions for audit trail.
"""

from database.connection import get_connection
from services.auth_service import get_current_user
from utils.helpers import get_current_timestamp


def log_action(action, module, details="", performed_by=None):
    """Record an activity log entry attributed to the active user."""
    if performed_by is None:
        current_user = get_current_user()
        performed_by = current_user["username"] if current_user else "system"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO activity_logs (action, module, details, performed_by, timestamp)
           VALUES (?, ?, ?, ?, ?)""",
        (action, module, details, performed_by, get_current_timestamp()),
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit=50):
    """Fetch the most recent activity logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_logs_by_module(module, limit=50):
    """Fetch activity logs filtered by module."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM activity_logs WHERE module = ? ORDER BY id DESC LIMIT ?",
        (module, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
