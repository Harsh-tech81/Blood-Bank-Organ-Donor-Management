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

    conn.commit()
    conn.close()

    # Seed default data
    from database.seed import seed_default_data
    seed_default_data()
