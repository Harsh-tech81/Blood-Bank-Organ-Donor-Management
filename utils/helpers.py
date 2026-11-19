"""
General helper/utility functions used across the application.
"""

from datetime import datetime


def get_current_timestamp() -> str:
    """Return the current date-time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date() -> str:
    """Return the current date as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d")


def format_date(date_str: str) -> str:
    """Format a date string for display (YYYY-MM-DD → DD/MM/YYYY)."""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return date_str


def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text with ellipsis if it exceeds max_length."""
    if not text:
        return ""
    return text if len(text) <= max_length else text[:max_length - 3] + "..."


def generate_id_prefix(module: str) -> str:
    """Generate a readable ID prefix for display (e.g., BD-001)."""
    prefixes = {
        "blood_donor": "BD",
        "organ_donor": "OD",
        "blood_request": "BR",
        "organ_request": "OR",
    }
    return prefixes.get(module, "XX")
