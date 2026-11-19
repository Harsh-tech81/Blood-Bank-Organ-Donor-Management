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
    "primary": "#1f6aa5",
    "secondary": "#2b2b2b",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "sidebar_bg": "#1a1a2e",
    "sidebar_hover": "#16213e",
    "sidebar_active": "#0f3460",
    "card_bg": "#2b2b2b",
}

# ─── Database ────────────────────────────────────────────────────
DB_NAME = "bloodbank.db"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"  # Will be hashed before storing


def get_app_data_dir() -> str:
    """Get the application data directory for storing the database."""
    try:
        if sys.platform == "win32":
            app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            data_dir = os.path.join(app_data, "BloodBankManager")
        else:
            data_dir = os.path.join(os.path.expanduser("~"), ".bloodbankmanager")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    except (PermissionError, OSError):
        # Fallback to local directory if AppData is not accessible/writable
        local_dir = os.path.join(os.path.abspath("."), "data")
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
