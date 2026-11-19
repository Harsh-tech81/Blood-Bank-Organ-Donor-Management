"""
Blood donor model — CRUD operations for blood_donors and blood_donations tables.
"""

from database.connection import get_connection
from utils.helpers import get_current_timestamp


# ─── Blood Donors ────────────────────────────────────────────────

def add_donor(name, age, gender, blood_group, phone="", email="", address=""):
    """Add a new blood donor. Returns the new donor ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO blood_donors (name, age, gender, blood_group, phone, email, address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, int(age), gender, blood_group, phone, email, address),
    )
    conn.commit()
    donor_id = cursor.lastrowid
    conn.close()
    return donor_id


def get_all_donors():
    """Fetch all blood donors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_donors ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_donor_by_id(donor_id):
    """Fetch a single donor by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_donors WHERE id = ?", (donor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_donor(donor_id, name, age, gender, blood_group, phone="", email="", address=""):
    """Update an existing blood donor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE blood_donors
           SET name=?, age=?, gender=?, blood_group=?, phone=?, email=?, address=?
           WHERE id=?""",
        (name, int(age), gender, blood_group, phone, email, address, donor_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_donor(donor_id):
    """Delete a blood donor by ID (cascades to donations)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blood_donors WHERE id = ?", (donor_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def search_donors(name="", blood_group=""):
    """Search donors by name and/or blood group."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM blood_donors WHERE 1=1"
    params = []

    if name and name.strip():
        query += " AND name LIKE ?"
        params.append(f"%{name.strip()}%")
    if blood_group and blood_group.strip() and blood_group != "All":
        query += " AND blood_group = ?"
        params.append(blood_group.strip())

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_donor_count():
    """Get total number of blood donors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blood_donors")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ─── Blood Donations ────────────────────────────────────────────

def record_donation(donor_id, units=1, notes=""):
    """Record a blood donation for a donor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO blood_donations (donor_id, donation_date, units, notes)
           VALUES (?, ?, ?, ?)""",
        (donor_id, get_current_timestamp(), units, notes),
    )
    conn.commit()
    donation_id = cursor.lastrowid
    conn.close()
    return donation_id


def get_donation_history(donor_id):
    """Get all donations for a specific donor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM blood_donations WHERE donor_id = ? ORDER BY donation_date DESC",
        (donor_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_donations():
    """Get total number of donations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blood_donations")
    count = cursor.fetchone()[0]
    conn.close()
    return count
