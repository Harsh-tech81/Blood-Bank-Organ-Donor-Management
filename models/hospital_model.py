"""Persistence helpers for normalized hospital records."""

from database.connection import get_connection


def get_or_create_hospital(name):
    """Return a hospital ID, reusing an existing record case-insensitively."""
    normalized_name = (name or "").strip()
    if not normalized_name:
        return None
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM hospitals WHERE name = ? COLLATE NOCASE",
            (normalized_name,),
        ).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO hospitals (name) VALUES (?)", (normalized_name,)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_hospitals():
    """Return hospitals ordered alphabetically."""
    conn = get_connection()
    try:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM hospitals ORDER BY name"
        ).fetchall()]
    finally:
        conn.close()
