"""Queries for organ donor-to-recipient allocation history."""

from database.connection import get_connection


def get_all_allocations():
    """Return allocation history with donor, recipient, and hospital names."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, d.name AS donor_name, r.name AS recipient_name,
                      h.name AS hospital_name, o.organ_type
               FROM organ_allocations a
               JOIN organ_donors d ON d.id = a.donor_id
               LEFT JOIN recipients r ON r.id = a.recipient_id
               LEFT JOIN hospitals h ON h.id = a.hospital_id
               JOIN organ_requests o ON o.id = a.organ_request_id
               ORDER BY a.id DESC"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
