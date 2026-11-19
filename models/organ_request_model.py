"""
Organ request model — CRUD operations for organ_requests table.
Supports strict triage ordering (Critical -> Urgent -> Normal) so
high-need patients are prioritized at the top.
"""

import sqlite3

from database.connection import get_connection
from models.hospital_model import get_or_create_hospital
from models.recipient_model import get_or_create_recipient

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
    recipient_id = get_or_create_recipient(patient_name, blood_group)
    hospital_id = get_or_create_hospital(hospital)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO organ_requests
           (recipient_id, hospital_id, patient_name, organ_type, blood_group, hospital, urgency)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (recipient_id, hospital_id, patient_name, organ_type, blood_group, hospital, urgency),
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


def transition_organ_request_status(request_id, new_status):
    """
    Transition an organ request and its donor reservation atomically.

    Matching reserves one eligible donor and persists that donor on the request.
    Fulfillment verifies the persisted reservation before marking both records
    complete. Returns (success, message, donor) where donor is the affected
    donor row when applicable.
    """
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            "SELECT * FROM organ_requests WHERE id = ?", (request_id,)
        ).fetchone()
        if not request:
            conn.rollback()
            return False, "Organ request record not found.", None

        current_status = request["status"]
        donor = None

        if new_status == "Matched":
            if current_status != "Pending":
                conn.rollback()
                return False, f"Only pending requests can be matched (current status: '{current_status}').", None

            donor = conn.execute(
                """SELECT * FROM organ_donors
                   WHERE organ_type = ?
                     AND (? = '' OR blood_group = ?)
                     AND consent_status = 'Consented'
                     AND status = 'Available'
                   ORDER BY id DESC
                   LIMIT 1""",
                (request["organ_type"], request["blood_group"] or "",
                 request["blood_group"] or ""),
            ).fetchone()
            if not donor:
                conn.rollback()
                return False, (
                    f"Cannot set to 'Matched': No active, legally consented donor "
                    f"found for {request['organ_type']} (Blood: "
                    f"{request['blood_group'] or 'Any'})."
                ), None

            donor_update = conn.execute(
                """UPDATE organ_donors
                   SET status = 'Matched'
                   WHERE id = ? AND consent_status = 'Consented' AND status = 'Available'""",
                (donor["id"],),
            )
            request_update = conn.execute(
                """UPDATE organ_requests
                   SET status = 'Matched', matched_donor_id = ?
                   WHERE id = ? AND status = 'Pending' AND matched_donor_id IS NULL""",
                (donor["id"], request_id),
            )
            if donor_update.rowcount != 1 or request_update.rowcount != 1:
                raise sqlite3.IntegrityError("The donor reservation could not be secured.")
            conn.execute(
                """INSERT INTO organ_allocations
                   (organ_request_id, donor_id, recipient_id, hospital_id, status)
                   VALUES (?, ?, ?, ?, 'Reserved')""",
                (request_id, donor["id"], request["recipient_id"], request["hospital_id"]),
            )

        elif new_status == "Fulfilled":
            if current_status != "Matched" or not request["matched_donor_id"]:
                conn.rollback()
                return False, (
                    "Cannot set to 'Fulfilled': the request must have a verified "
                    "matched donor reservation."
                ), None

            donor = conn.execute(
                "SELECT * FROM organ_donors WHERE id = ?",
                (request["matched_donor_id"],),
            ).fetchone()
            if (
                not donor
                or donor["organ_type"] != request["organ_type"]
                or (request["blood_group"] and donor["blood_group"] != request["blood_group"])
                or donor["consent_status"] != "Consented"
                or donor["status"] != "Matched"
            ):
                conn.rollback()
                return False, (
                    "Cannot set to 'Fulfilled': the reserved donor is no longer "
                    "available or consented."
                ), None

            donor_update = conn.execute(
                "UPDATE organ_donors SET status = 'Donated' "
                "WHERE id = ? AND status = 'Matched' AND consent_status = 'Consented'",
                (donor["id"],),
            )
            request_update = conn.execute(
                "UPDATE organ_requests SET status = 'Fulfilled' "
                "WHERE id = ? AND status = 'Matched' AND matched_donor_id = ?",
                (request_id, donor["id"]),
            )
            if donor_update.rowcount != 1 or request_update.rowcount != 1:
                raise sqlite3.IntegrityError("The donor reservation could not be fulfilled.")
            allocation_update = conn.execute(
                """UPDATE organ_allocations
                   SET status = 'Fulfilled', fulfilled_on = CURRENT_TIMESTAMP
                   WHERE organ_request_id = ? AND donor_id = ? AND status = 'Reserved'""",
                (request_id, donor["id"]),
            )
            if allocation_update.rowcount != 1:
                raise sqlite3.IntegrityError("The organ allocation history could not be completed.")

        elif new_status == "Rejected" and current_status == "Matched":
            if request["matched_donor_id"]:
                conn.execute(
                    "UPDATE organ_donors SET status = 'Available' "
                    "WHERE id = ? AND status = 'Matched'",
                    (request["matched_donor_id"],),
                )
                conn.execute(
                    """UPDATE organ_allocations SET status = 'Cancelled'
                       WHERE organ_request_id = ? AND donor_id = ? AND status = 'Reserved'""",
                    (request_id, request["matched_donor_id"]),
                )
            conn.execute(
                "UPDATE organ_requests SET status = 'Rejected', matched_donor_id = NULL "
                "WHERE id = ? AND status = 'Matched'",
                (request_id,),
            )
        else:
            updated = conn.execute(
                "UPDATE organ_requests SET status = ? WHERE id = ?",
                (new_status, request_id),
            )
            if updated.rowcount != 1:
                raise sqlite3.IntegrityError("The organ request status could not be updated.")

        conn.commit()
        return True, "", donor
    except sqlite3.Error as exc:
        conn.rollback()
        return False, f"Failed to update organ request status: {exc}", None
    finally:
        conn.close()


def delete_organ_request(request_id):
    """Delete an organ request by ID."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            "SELECT status, matched_donor_id FROM organ_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        if not request:
            conn.rollback()
            return False

        if request["status"] == "Matched" and request["matched_donor_id"]:
            conn.execute(
                "UPDATE organ_donors SET status = 'Available' "
                "WHERE id = ? AND status = 'Matched'",
                (request["matched_donor_id"],),
            )
        conn.execute("DELETE FROM organ_requests WHERE id = ?", (request_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()


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
