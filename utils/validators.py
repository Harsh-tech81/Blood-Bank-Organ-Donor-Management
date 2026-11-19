"""
Input validation functions for form data.
Returns (is_valid: bool, error_message: str).
"""

import re
from utils.constants import BLOOD_GROUPS, GENDERS, ORGAN_TYPES


def validate_name(name: str) -> tuple[bool, str]:
    """Validate a person's name."""
    if not name or not name.strip():
        return False, "Name is required."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."
    if len(name.strip()) > 100:
        return False, "Name must be less than 100 characters."
    if not re.match(r'^[a-zA-Z\s.\'-]+$', name.strip()):
        return False, "Name can only contain letters, spaces, dots, hyphens, and apostrophes."
    return True, ""


def validate_age(age_str: str) -> tuple[bool, str]:
    """Validate age (must be 18-65 for blood donors)."""
    if not age_str or not age_str.strip():
        return False, "Age is required."
    try:
        age = int(age_str.strip())
    except ValueError:
        return False, "Age must be a number."
    if age < 1 or age > 120:
        return False, "Age must be between 1 and 120."
    return True, ""


def validate_donor_age(age_str: str) -> tuple[bool, str]:
    """Validate blood donor age (must be 18-65)."""
    valid, msg = validate_age(age_str)
    if not valid:
        return valid, msg
    age = int(age_str.strip())
    if age < 18 or age > 65:
        return False, "Blood donor age must be between 18 and 65."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number."""
    if not phone or not phone.strip():
        return True, ""  # Phone is optional
    phone = phone.strip()
    # Allow digits, spaces, dashes, plus, parentheses
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if not cleaned.isdigit():
        return False, "Phone number can only contain digits, spaces, dashes, and parentheses."
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Phone number must be 10-15 digits."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address."""
    if not email or not email.strip():
        return True, ""  # Email is optional
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format."
    return True, ""


def validate_blood_group(blood_group: str) -> tuple[bool, str]:
    """Validate blood group selection."""
    if not blood_group or blood_group.strip() not in BLOOD_GROUPS:
        return False, f"Please select a valid blood group: {', '.join(BLOOD_GROUPS)}"
    return True, ""


def validate_gender(gender: str) -> tuple[bool, str]:
    """Validate gender selection."""
    if not gender or gender.strip() not in GENDERS:
        return False, f"Please select a valid gender: {', '.join(GENDERS)}"
    return True, ""


def validate_organ_type(organ_type: str) -> tuple[bool, str]:
    """Validate organ type selection."""
    if not organ_type or organ_type.strip() not in ORGAN_TYPES:
        return False, f"Please select a valid organ type."
    return True, ""


def validate_required(value: str, field_name: str) -> tuple[bool, str]:
    """Validate that a required field is not empty."""
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, ""


def validate_positive_integer(value: str, field_name: str) -> tuple[bool, str]:
    """Validate that a value is a positive integer."""
    if not value or not value.strip():
        return False, f"{field_name} is required."
    try:
        num = int(value.strip())
    except ValueError:
        return False, f"{field_name} must be a number."
    if num < 1:
        return False, f"{field_name} must be at least 1."
    return True, ""
