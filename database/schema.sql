-- ============================================
-- Blood Bank & Organ Donors Management System
-- Database Schema — SQLite
-- ============================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
        CHECK(role IN ('Administrator', 'Medical Staff', 'Medical Officer', 'admin')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER CHECK(age IS NULL OR (age >= 0 AND age <= 130)),
    gender TEXT CHECK(gender IS NULL OR gender IN ('Male', 'Female', 'Other')),
    blood_group TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS blood_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    donation_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    units INTEGER NOT NULL DEFAULT 1 CHECK(units > 0),
    notes TEXT,
    FOREIGN KEY (donor_id) REFERENCES blood_donors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS blood_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_group TEXT UNIQUE NOT NULL,
    units_available INTEGER NOT NULL DEFAULT 0 CHECK(units_available >= 0),
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blood_inventory_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donation_id INTEGER,
    inventory_id INTEGER NOT NULL,
    blood_group TEXT NOT NULL,
    units_received INTEGER NOT NULL CHECK(units_received > 0),
    units_remaining INTEGER NOT NULL CHECK(units_remaining >= 0 AND units_remaining <= units_received),
    collection_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available'
        CHECK(status IN ('Available', 'Exhausted', 'Expired')),
    FOREIGN KEY (donation_id) REFERENCES blood_donations(id) ON DELETE SET NULL,
    FOREIGN KEY (inventory_id) REFERENCES blood_inventory(id) ON DELETE RESTRICT
);

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
    review_status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(review_status IN ('Pending', 'Under Review', 'Verified', 'Rejected', 'Expired')),
    status TEXT NOT NULL DEFAULT 'Available'
        CHECK(status IN ('Available', 'Matched', 'Donated', 'Unavailable')),
    registered_on TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blood_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER,
    hospital_id INTEGER,
    patient_name TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    units_needed INTEGER NOT NULL DEFAULT 1 CHECK(units_needed > 0),
    hospital TEXT,
    urgency TEXT NOT NULL DEFAULT 'Normal'
        CHECK(urgency IN ('Normal', 'Urgent', 'Critical')),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Approved', 'Fulfilled', 'Rejected')),
    requested_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE SET NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS organ_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER,
    hospital_id INTEGER,
    patient_name TEXT NOT NULL,
    organ_type TEXT NOT NULL,
    blood_group TEXT,
    hospital TEXT,
    urgency TEXT NOT NULL DEFAULT 'Normal'
        CHECK(urgency IN ('Normal', 'Urgent', 'Critical')),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Proposed', 'Matched', 'Fulfilled', 'Rejected')),
    review_status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(review_status IN ('Pending', 'Under Review', 'Approved', 'Rejected')),
    matched_donor_id INTEGER,
    requested_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE SET NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (matched_donor_id) REFERENCES organ_donors(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS organ_allocations (
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
);

CREATE TABLE IF NOT EXISTS organ_donor_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    review_type TEXT NOT NULL DEFAULT 'Eligibility Documentation',
    decision TEXT NOT NULL
        CHECK(decision IN ('Under Review', 'Verified', 'Rejected', 'Expired')),
    notes TEXT NOT NULL,
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES organ_donors(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS organ_request_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    decision TEXT NOT NULL
        CHECK(decision IN ('Under Review', 'Approved', 'Rejected')),
    notes TEXT NOT NULL,
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES organ_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS transplant_authorizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organ_request_id INTEGER NOT NULL,
    donor_id INTEGER NOT NULL,
    recipient_id INTEGER,
    hospital_id INTEGER,
    authority_name TEXT NOT NULL,
    reference_number TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Approved', 'Denied', 'Revoked', 'Expired')),
    authorized_by INTEGER,
    authorized_at TEXT,
    expires_at TEXT,
    notes TEXT NOT NULL,
    FOREIGN KEY (organ_request_id) REFERENCES organ_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES organ_donors(id) ON DELETE RESTRICT,
    FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE SET NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (authorized_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS organ_allocation_events (
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
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    details TEXT,
    performed_by TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_blood_batches_fifo
    ON blood_inventory_batches (blood_group, expiry_date, id);
CREATE INDEX IF NOT EXISTS idx_blood_requests_recipient
    ON blood_requests (recipient_id);
CREATE INDEX IF NOT EXISTS idx_blood_requests_hospital
    ON blood_requests (hospital_id);
CREATE INDEX IF NOT EXISTS idx_organ_requests_recipient
    ON organ_requests (recipient_id);
CREATE INDEX IF NOT EXISTS idx_organ_requests_hospital
    ON organ_requests (hospital_id);
CREATE INDEX IF NOT EXISTS idx_organ_allocations_request
    ON organ_allocations (organ_request_id);
CREATE INDEX IF NOT EXISTS idx_organ_donor_reviews_donor
    ON organ_donor_reviews (donor_id, reviewed_at);
CREATE INDEX IF NOT EXISTS idx_organ_request_reviews_request
    ON organ_request_reviews (request_id, reviewed_at);
CREATE INDEX IF NOT EXISTS idx_transplant_authorizations_request
    ON transplant_authorizations (organ_request_id, status);
CREATE INDEX IF NOT EXISTS idx_allocation_events_allocation
    ON organ_allocation_events (allocation_id, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_organ_allocation
    ON organ_allocations (organ_request_id)
    WHERE status IN ('Proposed', 'Authority Approved', 'Reserved', 'Fulfilled');
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_approved_transplant_authorization
    ON transplant_authorizations (organ_request_id)
    WHERE status = 'Approved';
