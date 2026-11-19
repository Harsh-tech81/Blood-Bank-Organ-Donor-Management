"""
Application-wide configuration and settings.
Blood Bank & Organ Donors Management System
"""

import sys
import os

# ─── App Metadata ────────────────────────────────────────────────
APP_NAME = "Blood Bank & Organ Donors Management System"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Team BloodBank"

# ─── Window Settings ─────────────────────────────────────────────
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600

# ─── UI Theme ────────────────────────────────────────────────────
APPEARANCE_MODE = "dark"       # "dark", "light", or "system"
COLOR_THEME = "blue"           # CustomTkinter color theme

# ─── Sidebar Config ──────────────────────────────────────────────
SIDEBAR_WIDTH = 220

# ─── Colors ──────────────────────────────────────────────────────
COLORS = {
    "primary": "#2563eb",         # Vibrant Royal Blue
    "primary_hover": "#1d4ed8",
    "secondary": "#1e293b",       # Slate 800
    "accent_red": "#e11d48",      # Crimson / Blood red
    "accent_red_hover": "#be123c",
    "accent_emerald": "#059669",  # Emerald Green
    "accent_emerald_hover": "#047857",
    "accent_purple": "#7c3aed",   # Violet
    "accent_purple_hover": "#6d28d9",
    "accent_amber": "#d97706",    # Amber
    "success": "#10b981",         # Mint Success
    "danger": "#ef4444",          # Rose Danger
    "warning": "#f59e0b",         # Warning Yellow
    "info": "#06b6d4",            # Cyan Info
    "light": "#f8fafc",
    "dark": "#0f172a",            # Deep background
    "bg_main": "#0b0f19",         # Ultra-deep dark canvas
    "surface": "#131b2e",         # Elevated card surface
    "surface_border": "#1e293b",  # Sleek border
    "surface_hover": "#1c2640",
    "sidebar_bg": "#0d1322",      # Deep sidebar
    "sidebar_hover": "#1e293b",
    "sidebar_active": "#2563eb",  # Active tab glow
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

# ─── Database ────────────────────────────────────────────────────
DB_NAME = "bloodbank.db"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Staff account (pre-seeded for role demonstration)
DEFAULT_STAFF_USERNAME = "staff"
DEFAULT_STAFF_PASSWORD = "staff123"


def get_app_data_dir() -> str:
    """Get the application data directory for storing the database."""
    try:
        if sys.platform == "win32":
            app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            data_dir = os.path.join(app_data, "BloodBankManager")
        else:
            data_dir = os.path.join(os.path.expanduser("~"), ".bloodbankmanager")
        os.makedirs(data_dir, exist_ok=True)
        # Test writability by checking if a dummy test file can be touched
        test_file = os.path.join(data_dir, ".perm_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return data_dir
    except (PermissionError, OSError, Exception):
        # Fallback to local data directory if AppData is not accessible/writable
        local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(local_dir, exist_ok=True)
        return local_dir


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to a bundled resource.
    Works for both dev mode and PyInstaller .exe.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
