"""
Organ donor model — CRUD operations for the organ_donors table.
"""

from database.connection import get_connection


def add_organ_donor(name, age, gender, blood_group, organ_type, phone="",
                    email="", address="", consent_status="Pending"):
    """Add a new organ donor. Returns the new donor ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO organ_donors
           (name, age, gender, blood_group, organ_type, phone, email, address, consent_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, int(age), gender, blood_group, organ_type, phone, email, address, consent_status),
    )
    conn.commit()
    donor_id = cursor.lastrowid
    conn.close()
    return donor_id


def get_all_organ_donors():
    """Fetch all organ donors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organ_donors ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_organ_donor_by_id(donor_id):
    """Fetch a single organ donor by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organ_donors WHERE id = ?", (donor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_organ_donor(donor_id, name, age, gender, blood_group, organ_type,
                       phone="", email="", address="", consent_status="Pending",
                       status="Available"):
    """Update an existing organ donor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE organ_donors
           SET name=?, age=?, gender=?, blood_group=?, organ_type=?,
               phone=?, email=?, address=?, consent_status=?, status=?
           WHERE id=?""",
        (name, int(age), gender, blood_group, organ_type, phone, email,
         address, consent_status, status, donor_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_organ_donor(donor_id):
    """Delete an organ donor by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM organ_donors WHERE id = ?", (donor_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def search_organ_donors(name="", organ_type="", blood_group=""):
    """Search organ donors by name, organ type, and/or blood group."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM organ_donors WHERE 1=1"
    params = []

    if name and name.strip():
        query += " AND name LIKE ?"
        params.append(f"%{name.strip()}%")
    if organ_type and organ_type.strip() and organ_type != "All":
        query += " AND organ_type = ?"
        params.append(organ_type.strip())
    if blood_group and blood_group.strip() and blood_group != "All":
        query += " AND blood_group = ?"
        params.append(blood_group.strip())

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_organ_donor_count():
    """Get total number of organ donors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM organ_donors")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def update_consent_status(donor_id, consent_status):
    """Update the consent status of an organ donor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE organ_donors SET consent_status = ? WHERE id = ?",
        (consent_status, donor_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_by_organ_type(organ_type):
    """Get all organ donors for a specific organ type."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM organ_donors WHERE organ_type = ? ORDER BY id DESC",
        (organ_type,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
