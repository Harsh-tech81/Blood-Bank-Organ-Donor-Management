"""
Blood request model — CRUD operations for blood_requests table.
Supports strict triage ordering (Critical -> Urgent -> Normal) so
high-need patients are prioritized at the top.
"""

import sqlite3

from database.connection import get_connection

# SQL CASE statement to sort by medical urgency priority
URGENCY_ORDER_SQL = """
CASE urgency
    WHEN 'Critical' THEN 1
    WHEN 'Urgent' THEN 2
    WHEN 'Normal' THEN 3
    ELSE 4
END,
CASE status
    WHEN 'Pending' THEN 1
    WHEN 'Approved' THEN 2
    WHEN 'Fulfilled' THEN 3
    WHEN 'Rejected' THEN 4
    ELSE 5
END,
id DESC
"""


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
    """Fetch all blood requests prioritized by Critical/Urgent status first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM blood_requests ORDER BY {URGENCY_ORDER_SQL}")
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


def fulfill_blood_request(request_id):
    """
    Deduct inventory and fulfill a blood request atomically.

    Both updates use the same transaction so a failed request update cannot
    leave inventory permanently reduced.
    """
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            "SELECT blood_group, units_needed, status FROM blood_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        if not request:
            conn.rollback()
            return False, "Request record not found."

        if request["status"] == "Fulfilled":
            conn.rollback()
            return True, ""

        inventory = conn.execute(
            "SELECT units_available FROM blood_inventory WHERE blood_group = ?",
            (request["blood_group"],),
        ).fetchone()
        available = inventory["units_available"] if inventory else 0
        if available < request["units_needed"]:
            conn.rollback()
            return False, (
                f"Cannot fulfill request: Only {available} unit(s) of "
                f"{request['blood_group']} available in inventory (Need "
                f"{request['units_needed']})."
            )

        inventory_update = conn.execute(
            """UPDATE blood_inventory
               SET units_available = units_available - ?, last_updated = CURRENT_TIMESTAMP
               WHERE blood_group = ? AND units_available >= ?""",
            (request["units_needed"], request["blood_group"], request["units_needed"]),
        )
        request_update = conn.execute(
            "UPDATE blood_requests SET status = 'Fulfilled' "
            "WHERE id = ? AND status = ?",
            (request_id, request["status"]),
        )
        if inventory_update.rowcount != 1 or request_update.rowcount != 1:
            raise sqlite3.IntegrityError("Blood fulfillment could not update both records.")

        conn.commit()
        return True, ""
    except sqlite3.Error as exc:
        conn.rollback()
        return False, f"Blood fulfillment failed: {exc}"
    finally:
        conn.close()


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
    """Search blood requests with triage order preserved."""
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

    query += f" ORDER BY {URGENCY_ORDER_SQL}"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
