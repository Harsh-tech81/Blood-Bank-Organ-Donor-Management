"""
Blood inventory model — CRUD operations for blood_inventory table.
"""

from database.connection import get_connection
from utils.helpers import get_current_timestamp


def get_all_inventory():
    """Fetch all blood inventory rows."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_inventory ORDER BY blood_group")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_inventory_by_blood_group(blood_group):
    """Fetch inventory for a specific blood group."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM blood_inventory WHERE blood_group = ?", (blood_group,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_stock(blood_group, units):
    """Set the units_available for a blood group."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE blood_inventory
           SET units_available = ?, last_updated = ?
           WHERE blood_group = ?""",
        (units, get_current_timestamp(), blood_group),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def increment_units(blood_group, units=1):
    """Add units to a blood group's stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE blood_inventory
           SET units_available = units_available + ?, last_updated = ?
           WHERE blood_group = ?""",
        (units, get_current_timestamp(), blood_group),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def decrement_units(blood_group, units=1):
    """Remove units from a blood group's stock (won't go below 0)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check current stock first
    cursor.execute(
        "SELECT units_available FROM blood_inventory WHERE blood_group = ?",
        (blood_group,),
    )
    row = cursor.fetchone()
    if not row or row[0] < units:
        conn.close()
        return False

    cursor.execute(
        """UPDATE blood_inventory
           SET units_available = units_available - ?, last_updated = ?
           WHERE blood_group = ?""",
        (units, get_current_timestamp(), blood_group),
    )
    conn.commit()
    conn.close()
    return True


def get_total_blood_units():
    """Get total blood units across all groups."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(units_available), 0) FROM blood_inventory")
    total = cursor.fetchone()[0]
    conn.close()
    return total
