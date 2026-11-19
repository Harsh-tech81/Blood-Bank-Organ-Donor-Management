"""Persistence helpers for normalized recipient records."""

from database.connection import get_connection


def get_or_create_recipient(name, blood_group=None):
    """Return a recipient ID, reusing an existing record by normalized name."""
    normalized_name = name.strip()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM recipients WHERE name = ? COLLATE NOCASE ORDER BY id LIMIT 1",
            (normalized_name,),
        ).fetchone()
        if row:
            if blood_group:
                conn.execute(
                    "UPDATE recipients SET blood_group = COALESCE(blood_group, ?) WHERE id = ?",
                    (blood_group, row["id"]),
                )
                conn.commit()
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO recipients (name, blood_group) VALUES (?, ?)",
            (normalized_name, blood_group),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_recipients():
    """Return recipients ordered by newest first."""
    conn = get_connection()
    try:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM recipients ORDER BY id DESC"
        ).fetchall()]
    finally:
        conn.close()
