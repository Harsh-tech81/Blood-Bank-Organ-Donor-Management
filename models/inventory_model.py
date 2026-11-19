"""
Blood inventory model — CRUD operations for blood_inventory table.
"""

from database.connection import get_connection
from utils.helpers import get_current_timestamp

DEFAULT_SHELF_LIFE_DAYS = 42


def _expire_batches(conn, blood_group=None):
    """Move expired remaining units out of aggregate stock."""
    params = []
    where = "units_remaining > 0 AND date(expiry_date) < date('now')"
    if blood_group:
        where += " AND blood_group = ?"
        params.append(blood_group)

    expired = conn.execute(
        f"""SELECT inventory_id, SUM(units_remaining) AS units
            FROM blood_inventory_batches
            WHERE {where}
            GROUP BY inventory_id""",
        params,
    ).fetchall()
    for row in expired:
        conn.execute(
            """UPDATE blood_inventory
               SET units_available = MAX(0, units_available - ?),
                   last_updated = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (row["units"], row["inventory_id"]),
        )

    conn.execute(
        f"""UPDATE blood_inventory_batches
            SET units_remaining = 0, status = 'Expired'
            WHERE {where}""",
        params,
    )


def _consume_batches(conn, blood_group, units):
    """Consume active batches FIFO and return any legacy units still needed."""
    remaining = units
    batches = conn.execute(
        """SELECT id, units_remaining
           FROM blood_inventory_batches
           WHERE blood_group = ? AND units_remaining > 0
             AND date(expiry_date) >= date('now')
           ORDER BY date(expiry_date), id""",
        (blood_group,),
    ).fetchall()
    for batch in batches:
        consumed = min(remaining, batch["units_remaining"])
        conn.execute(
            """UPDATE blood_inventory_batches
               SET units_remaining = units_remaining - ?,
                   status = CASE WHEN units_remaining - ? = 0
                                 THEN 'Exhausted' ELSE status END
               WHERE id = ?""",
            (consumed, consumed, batch["id"]),
        )
        remaining -= consumed
        if remaining == 0:
            break
    return remaining


def get_all_inventory():
    """Fetch all blood inventory rows."""
    conn = get_connection()
    try:
        _expire_batches(conn)
        conn.commit()
        rows = conn.execute(
            """SELECT i.*,
                      COALESCE((
                          SELECT SUM(b.units_remaining)
                          FROM blood_inventory_batches b
                          WHERE b.inventory_id = i.id
                            AND b.units_remaining > 0
                            AND date(b.expiry_date) >= date('now')
                      ), 0) AS batch_units_available,
                      (
                          SELECT MIN(b.expiry_date)
                          FROM blood_inventory_batches b
                          WHERE b.inventory_id = i.id
                            AND b.units_remaining > 0
                            AND date(b.expiry_date) >= date('now')
                      ) AS next_expiry_date
               FROM blood_inventory i
               ORDER BY i.blood_group"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_inventory_by_blood_group(blood_group):
    """Fetch inventory for a specific blood group."""
    conn = get_connection()
    try:
        _expire_batches(conn, blood_group)
        conn.commit()
        row = conn.execute(
            """SELECT i.*,
                      COALESCE((
                          SELECT SUM(b.units_remaining)
                          FROM blood_inventory_batches b
                          WHERE b.inventory_id = i.id
                            AND b.units_remaining > 0
                            AND date(b.expiry_date) >= date('now')
                      ), 0) AS batch_units_available,
                      (
                          SELECT MIN(b.expiry_date)
                          FROM blood_inventory_batches b
                          WHERE b.inventory_id = i.id
                            AND b.units_remaining > 0
                            AND date(b.expiry_date) >= date('now')
                      ) AS next_expiry_date
               FROM blood_inventory i
               WHERE i.blood_group = ?""",
            (blood_group,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_stock(blood_group, units):
    """Set the units_available for a blood group."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        _expire_batches(conn, blood_group)
        row = conn.execute(
            "SELECT id, units_available FROM blood_inventory WHERE blood_group = ?",
            (blood_group,),
        ).fetchone()
        if not row or units < 0:
            conn.rollback()
            return False
        if units > row["units_available"]:
            _insert_manual_batch(conn, row["id"], blood_group, units - row["units_available"])
        elif units < row["units_available"]:
            _consume_batches(conn, blood_group, row["units_available"] - units)
        updated = conn.execute(
            """UPDATE blood_inventory
               SET units_available = ?, last_updated = ?
               WHERE blood_group = ?""",
            (units, get_current_timestamp(), blood_group),
        )
        conn.commit()
        return updated.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def increment_units(blood_group, units=1):
    """Add units to a blood group's stock."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        _expire_batches(conn, blood_group)
        row = conn.execute(
            "SELECT id FROM blood_inventory WHERE blood_group = ?", (blood_group,)
        ).fetchone()
        if not row or units < 1:
            conn.rollback()
            return False
        _insert_manual_batch(conn, row["id"], blood_group, units)
        updated = conn.execute(
            """UPDATE blood_inventory
               SET units_available = units_available + ?, last_updated = ?
               WHERE blood_group = ?""",
            (units, get_current_timestamp(), blood_group),
        )
        conn.commit()
        return updated.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def decrement_units(blood_group, units=1):
    """Remove units from a blood group's stock (won't go below 0)."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        _expire_batches(conn, blood_group)
        row = conn.execute(
            "SELECT units_available FROM blood_inventory WHERE blood_group = ?",
            (blood_group,),
        ).fetchone()
        if not row or units < 1 or row["units_available"] < units:
            conn.rollback()
            return False
        _consume_batches(conn, blood_group, units)
        conn.execute(
            """UPDATE blood_inventory
               SET units_available = units_available - ?, last_updated = ?
               WHERE blood_group = ?""",
            (units, get_current_timestamp(), blood_group),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _insert_manual_batch(conn, inventory_id, blood_group, units):
    """Create a dated batch for stock entered through inventory management."""
    conn.execute(
        """INSERT INTO blood_inventory_batches
           (inventory_id, blood_group, units_received, units_remaining, expiry_date)
           VALUES (?, ?, ?, ?, date('now', ?))""",
        (inventory_id, blood_group, units, units,
         f"+{DEFAULT_SHELF_LIFE_DAYS} days"),
    )


def backfill_legacy_inventory_batches():
    """Assign a transition expiry date to aggregate stock from older databases."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        _expire_batches(conn)
        rows = conn.execute(
            """SELECT i.id, i.blood_group,
                      i.units_available - COALESCE(SUM(b.units_remaining), 0) AS units
               FROM blood_inventory i
               LEFT JOIN blood_inventory_batches b
                 ON b.inventory_id = i.id AND b.units_remaining > 0
               GROUP BY i.id
               HAVING units > 0"""
        ).fetchall()
        for row in rows:
            _insert_manual_batch(conn, row["id"], row["blood_group"], row["units"])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_total_blood_units():
    """Get total blood units across all groups."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(units_available), 0) FROM blood_inventory")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_inventory_batches(blood_group=None, include_expired=False):
    """Return inventory batches, ordered by earliest expiry."""
    conn = get_connection()
    try:
        _expire_batches(conn, blood_group)
        conn.commit()
        query = """SELECT b.*, d.donation_date, bd.name AS donor_name
                   FROM blood_inventory_batches b
                   LEFT JOIN blood_donations d ON d.id = b.donation_id
                   LEFT JOIN blood_donors bd ON bd.id = d.donor_id
                   WHERE 1 = 1"""
        params = []
        if blood_group:
            query += " AND b.blood_group = ?"
            params.append(blood_group)
        if not include_expired:
            query += " AND b.status <> 'Expired'"
        query += " ORDER BY date(b.expiry_date), b.id"
        return [dict(row) for row in conn.execute(query, params).fetchall()]
    finally:
        conn.close()
