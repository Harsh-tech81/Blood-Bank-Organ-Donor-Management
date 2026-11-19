"""
Application-wide constants.
Centralized lists for dropdowns, validation, and display.
"""

# ─── Blood Groups ────────────────────────────────────────────────
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# ─── Gender Options ──────────────────────────────────────────────
GENDERS = ["Male", "Female", "Other"]

# ─── Organ Types ─────────────────────────────────────────────────
ORGAN_TYPES = [
    "Kidney",
    "Liver",
    "Heart",
    "Lungs",
    "Pancreas",
    "Cornea",
    "Bone Marrow",
    "Skin",
    "Intestine",
]

# ─── Urgency Levels ──────────────────────────────────────────────
URGENCY_LEVELS = ["Normal", "Urgent", "Critical"]

# ─── Request Statuses ────────────────────────────────────────────
BLOOD_REQUEST_STATUSES = ["Pending", "Approved", "Fulfilled", "Rejected"]
ORGAN_REQUEST_STATUSES = ["Pending", "Proposed", "Matched", "Fulfilled", "Rejected"]

# ─── Consent Statuses (Organ Donors) ────────────────────────────
CONSENT_STATUSES = ["Pending", "Consented", "Withdrawn"]

# ─── Organ Donor Statuses ────────────────────────────────────────
ORGAN_DONOR_STATUSES = ["Available", "Matched", "Donated", "Unavailable"]

# ─── Sidebar Menu Items ─────────────────────────────────────────
SIDEBAR_MENU = [
    {"label": "📊  Dashboard",       "key": "dashboard"},
    {"label": "🩸  Blood Donors",    "key": "blood_donors"},
    {"label": "📦  Blood Inventory", "key": "blood_inventory"},
    {"label": "🫀  Organ Donors",    "key": "organ_donors"},
    {"label": "📋  Blood Requests",  "key": "blood_requests"},
    {"label": "📝  Organ Requests",  "key": "organ_requests"},
    {"label": "📄  Reports",         "key": "reports"},
]

# ─── Table Column Configs ────────────────────────────────────────
DONOR_TABLE_COLUMNS = [
    ("ID", 50),
    ("Name", 150),
    ("Age", 50),
    ("Gender", 80),
    ("Blood Group", 100),
    ("Phone", 120),
    ("Email", 170),
    ("Registered On", 120),
]

ORGAN_DONOR_TABLE_COLUMNS = [
    ("ID", 50),
    ("Name", 150),
    ("Age", 50),
    ("Gender", 80),
    ("Blood Group", 100),
    ("Organ", 100),
    ("Consent", 90),
    ("Review", 90),
    ("Status", 90),
    ("Registered On", 120),
]

BLOOD_REQUEST_TABLE_COLUMNS = [
    ("ID", 50),
    ("Patient", 150),
    ("Blood Group", 100),
    ("Units", 60),
    ("Hospital", 150),
    ("Urgency", 80),
    ("Status", 90),
    ("Requested On", 120),
]

ORGAN_REQUEST_TABLE_COLUMNS = [
    ("ID", 50),
    ("Patient", 150),
    ("Organ", 100),
    ("Blood Group", 100),
    ("Hospital", 150),
    ("Urgency", 80),
    ("Status", 90),
    ("Requested On", 120),
]

INVENTORY_TABLE_COLUMNS = [
    ("ID", 50),
    ("Blood Group", 150),
    ("Units Available", 150),
    ("Next Expiry", 120),
    ("Batch Units", 100),
    ("Last Updated", 200),
]
