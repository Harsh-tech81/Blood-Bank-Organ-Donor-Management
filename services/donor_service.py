"""
Blood donor service — business logic layer.
Wraps model calls with validation and activity logging.
"""

from models.donor_model import (
    add_donor, get_all_donors, get_donor_by_id, update_donor,
    delete_donor, search_donors, record_donation,
)
from models.inventory_model import increment_units
from models.activity_log_model import log_action
from utils.validators import (
    validate_name, validate_donor_age, validate_blood_group,
    validate_gender, validate_phone, validate_email,
)


def create_donor(name, age, gender, blood_group, phone="", email="", address=""):
    """Validate and create a new blood donor."""
    # Validation
    validations = [
        validate_name(name),
        validate_donor_age(str(age)),
        validate_gender(gender),
        validate_blood_group(blood_group),
        validate_phone(phone),
        validate_email(email),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    donor_id = add_donor(name.strip(), int(age), gender, blood_group,
                         phone.strip(), email.strip(), address.strip())
    log_action("Created blood donor", "blood_donors",
               f"Donor: {name.strip()} ({blood_group})")
    return True, f"Blood donor added successfully (ID: {donor_id})"


def edit_donor(donor_id, name, age, gender, blood_group, phone="", email="", address=""):
    """Validate and update a blood donor."""
    validations = [
        validate_name(name),
        validate_donor_age(str(age)),
        validate_gender(gender),
        validate_blood_group(blood_group),
        validate_phone(phone),
        validate_email(email),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    success = update_donor(donor_id, name.strip(), int(age), gender, blood_group,
                           phone.strip(), email.strip(), address.strip())
    if success:
        log_action("Updated blood donor", "blood_donors",
                   f"Donor ID: {donor_id}")
    return success, "Blood donor updated successfully" if success else "Failed to update donor"


def remove_donor(donor_id):
    """Delete a blood donor."""
    success = delete_donor(donor_id)
    if success:
        log_action("Deleted blood donor", "blood_donors",
                   f"Donor ID: {donor_id}")
    return success


def add_donation(donor_id, blood_group, units=1, notes=""):
    """Record a donation and update inventory."""
    donation_id = record_donation(donor_id, units, notes)
    increment_units(blood_group, units)
    log_action("Recorded blood donation", "blood_donations",
               f"Donor ID: {donor_id}, Units: {units}, Group: {blood_group}")
    return donation_id


def list_donors(name="", blood_group=""):
    """List donors with optional search filters."""
    if name or (blood_group and blood_group != "All"):
        return search_donors(name, blood_group)
    return get_all_donors()
