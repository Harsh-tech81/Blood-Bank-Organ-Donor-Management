"""
Blood request model — CRUD operations for blood_requests table.
"""

from database.connection import get_connection


def add_blood_request(patient_name, blood_group, units_needed=1,
                      hospital="", urgency="Normal"):
    """Add a new blood request. Returns the new request ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO blood_requests
           (patient_name, blood_group, units_needed, hospital, urgency)
           VALUES (?, ?, ?, ?, ?)""",
        (patient_name, blood_group, int(units_needed), hospital, urgency),
    )
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id


def get_all_blood_requests():
    """Fetch all blood requests."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_requests ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_blood_request_by_id(request_id):
    """Fetch a single blood request by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_requests WHERE id = ?", (request_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_blood_request_status(request_id, status):
    """Update the status of a blood request."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE blood_requests SET status = ? WHERE id = ?",
        (status, request_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_blood_request(request_id):
    """Delete a blood request by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blood_requests WHERE id = ?", (request_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_pending_blood_requests_count():
    """Get count of pending blood requests."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blood_requests WHERE status = 'Pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def search_blood_requests(patient_name="", blood_group="", status=""):
    """Search blood requests by filters."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM blood_requests WHERE 1=1"
    params = []

    if patient_name and patient_name.strip():
        query += " AND patient_name LIKE ?"
        params.append(f"%{patient_name.strip()}%")
    if blood_group and blood_group.strip() and blood_group != "All":
        query += " AND blood_group = ?"
        params.append(blood_group.strip())
    if status and status.strip() and status != "All":
        query += " AND status = ?"
        params.append(status.strip())

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
