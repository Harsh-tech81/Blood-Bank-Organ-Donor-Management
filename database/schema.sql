-- ============================================
-- Blood Bank & Organ Donors Management System
-- Database Schema — SQLite
-- ============================================

-- 1. Users (Admin authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. Blood Donors
CREATE TABLE IF NOT EXISTS blood_donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER CHECK(age >= 18 AND age <= 65),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    blood_group TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    registered_on TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 3. Blood Donations (History — linked to donors)
CREATE TABLE IF NOT EXISTS blood_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    donation_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    units INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    FOREIGN KEY (donor_id) REFERENCES blood_donors(id) ON DELETE CASCADE
);

-- 4. Blood Inventory (One row per blood group)
CREATE TABLE IF NOT EXISTS blood_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_group TEXT UNIQUE NOT NULL,
    units_available INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 5. Organ Donors (With consent tracking)
CREATE TABLE IF NOT EXISTS organ_donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    blood_group TEXT,
    organ_type TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    consent_status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(consent_status IN ('Pending', 'Consented', 'Withdrawn')),
    status TEXT NOT NULL DEFAULT 'Available'
        CHECK(status IN ('Available', 'Matched', 'Donated', 'Unavailable')),
    registered_on TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 6. Blood Requests
CREATE TABLE IF NOT EXISTS blood_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    units_needed INTEGER NOT NULL DEFAULT 1,
    hospital TEXT,
    urgency TEXT NOT NULL DEFAULT 'Normal'
        CHECK(urgency IN ('Normal', 'Urgent', 'Critical')),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Approved', 'Fulfilled', 'Rejected')),
    requested_on TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 7. Organ Requests
CREATE TABLE IF NOT EXISTS organ_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    organ_type TEXT NOT NULL,
    blood_group TEXT,
    hospital TEXT,
    urgency TEXT NOT NULL DEFAULT 'Normal'
        CHECK(urgency IN ('Normal', 'Urgent', 'Critical')),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Matched', 'Fulfilled', 'Rejected')),
    matched_donor_id INTEGER,
    requested_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_donor_id) REFERENCES organ_donors(id)
);

-- 8. Activity Logs (Audit trail)
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    details TEXT,
    performed_by TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
