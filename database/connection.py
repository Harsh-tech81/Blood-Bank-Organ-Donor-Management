"""
Database connection manager.
Handles SQLite connection with proper path resolution
for both development and PyInstaller-bundled .exe.
"""

import os
import sys
import sqlite3

import config as app_config


def get_db_path() -> str:
    """
    Get the database file path.
    Stores DB in AppData/Local/BloodBankManager/ on Windows.
    """
    db_dir = app_config.get_app_data_dir()
    return os.path.join(db_dir, app_config.DB_NAME)


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with:
    - Foreign keys enabled
    - Row factory set to sqlite3.Row (access columns by name)
    """
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def get_schema_sql() -> str:
    """Read the schema.sql file (works in dev and .exe)."""
    schema_path = app_config.resource_path(os.path.join("database", "schema.sql"))
    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()


def initialize_db():
    """
    Initialize the database:
    1. Create all tables from schema.sql
    2. Seed default data (admin user, blood inventory)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables from schema.sql
    schema_sql = get_schema_sql()
    cursor.executescript(schema_sql)

    # Rebuild the pre-workflow allocation table so its status constraint can
    # represent proposals and authority approval without losing history.
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'organ_allocations'"
    )
    allocation_sql = cursor.fetchone()[0] or ""
    if "Proposed" not in allocation_sql:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name = 'organ_allocation_events'"
        )
        if cursor.fetchone():
            cursor.execute(
                "CREATE TABLE organ_allocation_events_legacy AS "
                "SELECT * FROM organ_allocation_events"
            )
            cursor.execute("DROP TABLE organ_allocation_events")
        cursor.execute(
            """CREATE TABLE organ_allocations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organ_request_id INTEGER NOT NULL,
                donor_id INTEGER NOT NULL,
                recipient_id INTEGER,
                hospital_id INTEGER,
                status TEXT NOT NULL DEFAULT 'Reserved'
                    CHECK(status IN ('Proposed', 'Authority Approved', 'Reserved',
                                     'Fulfilled', 'Rejected', 'Cancelled', 'Expired')),
                allocated_on TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fulfilled_on TEXT,
                notes TEXT,
                FOREIGN KEY (organ_request_id) REFERENCES organ_requests(id) ON DELETE CASCADE,
                FOREIGN KEY (donor_id) REFERENCES organ_donors(id) ON DELETE RESTRICT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE SET NULL,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
            )"""
        )
        cursor.execute(
            """INSERT INTO organ_allocations_new
               (id, organ_request_id, donor_id, recipient_id, hospital_id,
                status, allocated_on, fulfilled_on, notes)
               SELECT id, organ_request_id, donor_id, recipient_id, hospital_id,
                      status, allocated_on, fulfilled_on, notes
               FROM organ_allocations"""
        )
        cursor.execute("DROP TABLE organ_allocations")
        cursor.execute(
            "ALTER TABLE organ_allocations_new RENAME TO organ_allocations"
        )
        cursor.execute(
            """CREATE TABLE organ_allocation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                allocation_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT NOT NULL,
                actor_id INTEGER,
                notes TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (allocation_id) REFERENCES organ_allocations(id) ON DELETE CASCADE,
                FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL
            )"""
        )
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name = 'organ_allocation_events_legacy'"
        )
        if cursor.fetchone():
            cursor.execute(
                """INSERT INTO organ_allocation_events
                   (id, allocation_id, event_type, previous_status,
                    new_status, actor_id, notes, created_at)
                   SELECT id, allocation_id, event_type, previous_status,
                          new_status, actor_id, notes, created_at
                   FROM organ_allocation_events_legacy"""
            )
            cursor.execute("DROP TABLE organ_allocation_events_legacy")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_organ_allocations_request "
            "ON organ_allocations(organ_request_id)"
        )

    # Migrate databases created before recipient, hospital, and allocation
    # references were persisted. SQLite cannot add a foreign key to an
    # existing table, but nullable reference columns preserve old records.
    for table, column in (
        ("blood_requests", "recipient_id"),
        ("blood_requests", "hospital_id"),
        ("organ_requests", "recipient_id"),
        ("organ_requests", "hospital_id"),
        ("organ_donors", "review_status"),
        ("organ_requests", "review_status"),
    ):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        if column not in columns:
            if column.endswith("_id"):
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER")
            else:
                cursor.execute(
                    f"ALTER TABLE {table} ADD COLUMN {column} "
                    "TEXT NOT NULL DEFAULT 'Pending'"
                )

    # Migrate databases created before donor reservations were persisted.
    cursor.execute("PRAGMA table_info(organ_requests)")
    organ_request_columns = {row[1] for row in cursor.fetchall()}
    if "matched_donor_id" not in organ_request_columns:
        cursor.execute(
            "ALTER TABLE organ_requests ADD COLUMN matched_donor_id INTEGER "
            "REFERENCES organ_donors(id)"
        )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_organ_requests_matched_donor "
        "ON organ_requests(matched_donor_id)"
    )

    # Backfill normalized records without changing the legacy display fields.
    cursor.execute(
        """INSERT INTO recipients (name)
           SELECT DISTINCT patient_name FROM blood_requests br
           WHERE patient_name IS NOT NULL AND TRIM(patient_name) <> ''
             AND NOT EXISTS (
                 SELECT 1 FROM recipients r WHERE r.name = br.patient_name COLLATE NOCASE
             )"""
    )
    cursor.execute(
        """INSERT INTO recipients (name)
           SELECT DISTINCT patient_name FROM organ_requests orq
           WHERE patient_name IS NOT NULL AND TRIM(patient_name) <> ''
             AND NOT EXISTS (
                 SELECT 1 FROM recipients r WHERE r.name = orq.patient_name COLLATE NOCASE
             )"""
    )
    cursor.execute(
        """UPDATE blood_requests
           SET recipient_id = (
               SELECT id FROM recipients
               WHERE recipients.name = blood_requests.patient_name
               ORDER BY id LIMIT 1
           )
           WHERE recipient_id IS NULL"""
    )
    cursor.execute(
        """UPDATE organ_requests
           SET recipient_id = (
               SELECT id FROM recipients
               WHERE recipients.name = organ_requests.patient_name
               ORDER BY id LIMIT 1
           )
           WHERE recipient_id IS NULL"""
    )
    cursor.execute(
        """INSERT OR IGNORE INTO hospitals (name)
           SELECT DISTINCT TRIM(hospital) FROM blood_requests
           WHERE hospital IS NOT NULL AND TRIM(hospital) <> ''"""
    )
    cursor.execute(
        """INSERT OR IGNORE INTO hospitals (name)
           SELECT DISTINCT TRIM(hospital) FROM organ_requests
           WHERE hospital IS NOT NULL AND TRIM(hospital) <> ''"""
    )
    cursor.execute(
        """UPDATE blood_requests
           SET hospital_id = (
               SELECT id FROM hospitals
               WHERE hospitals.name = TRIM(blood_requests.hospital)
               ORDER BY id LIMIT 1
           )
           WHERE hospital_id IS NULL"""
    )
    cursor.execute(
        """UPDATE organ_requests
           SET hospital_id = (
               SELECT id FROM hospitals
               WHERE hospitals.name = TRIM(organ_requests.hospital)
               ORDER BY id LIMIT 1
           )
           WHERE hospital_id IS NULL"""
    )

    conn.commit()
    conn.close()

    # Seed default data
    from database.seed import seed_default_data
    seed_default_data()
