"""
Organ request model — CRUD operations for organ_requests table.
Supports strict triage ordering (Critical -> Urgent -> Normal) so
high-need patients are prioritized at the top.
"""

from database.connection import get_connection

URGENCY_ORDER_SQL = """
CASE urgency
    WHEN 'Critical' THEN 1
    WHEN 'Urgent' THEN 2
    WHEN 'Normal' THEN 3
    ELSE 4
END,
CASE status
    WHEN 'Pending' THEN 1
    WHEN 'Matched' THEN 2
    WHEN 'Fulfilled' THEN 3
    WHEN 'Rejected' THEN 4
    ELSE 5
END,
id DESC
"""


def add_organ_request(patient_name, organ_type, blood_group="",
                      hospital="", urgency="Normal"):
    """Add a new organ request. Returns the new request ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO organ_requests
           (patient_name, organ_type, blood_group, hospital, urgency)
           VALUES (?, ?, ?, ?, ?)""",
        (patient_name, organ_type, blood_group, hospital, urgency),
    )
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id


def get_all_organ_requests():
    """Fetch all organ requests ordered by clinical urgency."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM organ_requests ORDER BY {URGENCY_ORDER_SQL}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_organ_request_by_id(request_id):
    """Fetch a single organ request by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organ_requests WHERE id = ?", (request_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_organ_request_status(request_id, status):
    """Update the status of an organ request."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE organ_requests SET status = ? WHERE id = ?",
        (status, request_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_organ_request(request_id):
    """Delete an organ request by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM organ_requests WHERE id = ?", (request_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_pending_organ_requests_count():
    """Get count of pending organ requests."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM organ_requests WHERE status = 'Pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def search_organ_requests(patient_name="", organ_type="", status=""):
    """Search organ requests with triage priority preserved."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM organ_requests WHERE 1=1"
    params = []

    if patient_name and patient_name.strip():
        query += " AND patient_name LIKE ?"
        params.append(f"%{patient_name.strip()}%")
    if organ_type and organ_type.strip() and organ_type != "All":
        query += " AND organ_type = ?"
        params.append(organ_type.strip())
    if status and status.strip() and status != "All":
        query += " AND status = ?"
        params.append(status.strip())

    query += f" ORDER BY {URGENCY_ORDER_SQL}"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
