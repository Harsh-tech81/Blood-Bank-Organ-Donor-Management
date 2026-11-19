"""Persistence operations for organ review and authorization workflows."""

import sqlite3

from database.connection import get_connection


def record_donor_review(donor_id, reviewer_id, decision, notes):
    """Record a donor review and update its current workflow status."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        review = conn.execute(
            """INSERT INTO organ_donor_reviews
               (donor_id, reviewer_id, decision, notes)
               VALUES (?, ?, ?, ?)""",
            (donor_id, reviewer_id, decision, notes.strip()),
        )
        updated = conn.execute(
            "UPDATE organ_donors SET review_status = ? WHERE id = ?",
            (decision, donor_id),
        )
        if updated.rowcount != 1:
            raise sqlite3.IntegrityError("Organ donor record was not found.")
        conn.commit()
        return review.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_request_review(request_id, reviewer_id, decision, notes):
    """Record recipient/request review and update its current status."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        review = conn.execute(
            """INSERT INTO organ_request_reviews
               (request_id, reviewer_id, decision, notes)
               VALUES (?, ?, ?, ?)""",
            (request_id, reviewer_id, decision, notes.strip()),
        )
        updated = conn.execute(
            "UPDATE organ_requests SET review_status = ? WHERE id = ?",
            (decision, request_id),
        )
        if updated.rowcount != 1:
            raise sqlite3.IntegrityError("Organ request record was not found.")
        conn.commit()
        return review.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_transplant_authorization(
    request_id, donor_id, reviewer_id, authority_name, reference_number, notes
):
    """Record external transplant-authority approval; never infer it."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            """SELECT recipient_id, hospital_id, review_status FROM organ_requests
               WHERE id = ?""",
            (request_id,),
        ).fetchone()
        if not request:
            raise sqlite3.IntegrityError("Organ request record was not found.")
        donor = conn.execute(
            """SELECT id, consent_status, review_status FROM organ_donors
               WHERE id = ?""",
            (donor_id,),
        ).fetchone()
        if not donor:
            raise sqlite3.IntegrityError("Organ donor record was not found.")
        if request["review_status"] != "Approved":
            raise sqlite3.IntegrityError(
                "An approved recipient/request review is required first."
            )
        if donor["consent_status"] != "Consented" or donor["review_status"] != "Verified":
            raise sqlite3.IntegrityError(
                "Recorded consent and a completed donor review are required first."
            )
        proposal = conn.execute(
            """SELECT id FROM organ_allocations
               WHERE organ_request_id = ? AND donor_id = ? AND status = 'Proposed'""",
            (request_id, donor_id),
        ).fetchone()
        if not proposal:
            raise sqlite3.IntegrityError(
                "Create an allocation proposal before recording authority approval."
            )
        authorization = conn.execute(
            """INSERT INTO transplant_authorizations
               (organ_request_id, donor_id, recipient_id, hospital_id,
                authority_name, reference_number, status, authorized_by,
                authorized_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, 'Approved', ?, CURRENT_TIMESTAMP, ?)""",
            (
                request_id,
                donor_id,
                request["recipient_id"],
                request["hospital_id"],
                authority_name.strip(),
                reference_number.strip(),
                reviewer_id,
                notes.strip(),
            ),
        )
        proposal = conn.execute(
            """SELECT id, status FROM organ_allocations
               WHERE organ_request_id = ? AND donor_id = ?
                 AND status = 'Proposed'""",
            (request_id, donor_id),
        ).fetchone()
        if proposal:
            conn.execute(
                "UPDATE organ_allocations SET status = 'Authority Approved' WHERE id = ?",
                (proposal["id"],),
            )
            conn.execute(
                """INSERT INTO organ_allocation_events
                   (allocation_id, event_type, previous_status, new_status,
                    actor_id, notes)
                   VALUES (?, 'Authority Approval Recorded', ?, 'Authority Approved',
                           ?, ?)""",
                (
                    proposal["id"],
                    proposal["status"],
                    reviewer_id,
                    "External authority reference recorded; no clinical decision made.",
                ),
            )
        conn.commit()
        return authorization.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_latest_approved_authorization(request_id, donor_id=None):
    """Return the active external authorization for a proposed allocation."""
    conn = get_connection()
    try:
        query = """SELECT * FROM transplant_authorizations
                   WHERE organ_request_id = ? AND status = 'Approved'
                     AND (expires_at IS NULL OR date(expires_at) >= date('now'))"""
        params = [request_id]
        if donor_id is not None:
            query += " AND donor_id = ?"
            params.append(donor_id)
        query += " ORDER BY id DESC LIMIT 1"
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_latest_donor_review(donor_id):
    """Return the most recent donor review."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT * FROM organ_donor_reviews
               WHERE donor_id = ? ORDER BY id DESC LIMIT 1""",
            (donor_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_latest_request_review(request_id):
    """Return the most recent organ request review."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT * FROM organ_request_reviews
               WHERE request_id = ? ORDER BY id DESC LIMIT 1""",
            (request_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
