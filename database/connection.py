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

    # Migrate databases created before recipient, hospital, and allocation
    # references were persisted. SQLite cannot add a foreign key to an
    # existing table, but nullable reference columns preserve old records.
    for table, column in (
        ("blood_requests", "recipient_id"),
        ("blood_requests", "hospital_id"),
        ("organ_requests", "recipient_id"),
        ("organ_requests", "hospital_id"),
    ):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER")

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
