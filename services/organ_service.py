"""
Organ donor service — business logic layer.
"""

from models.organ_donor_model import (
    add_organ_donor, get_all_organ_donors, get_organ_donor_by_id,
    update_organ_donor, delete_organ_donor, search_organ_donors,
    update_consent_status,
)
from models.activity_log_model import log_action
from utils.validators import (
    validate_name, validate_age, validate_blood_group,
    validate_gender, validate_organ_type, validate_phone, validate_email,
)


def create_organ_donor(name, age, gender, blood_group, organ_type, phone="",
                       email="", address="", consent_status="Pending"):
    """Validate and create a new organ donor."""
    validations = [
        validate_name(name),
        validate_age(str(age)),
        validate_gender(gender),
        validate_blood_group(blood_group),
        validate_organ_type(organ_type),
        validate_phone(phone),
        validate_email(email),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    donor_id = add_organ_donor(
        name.strip(), int(age), gender, blood_group, organ_type,
        phone.strip(), email.strip(), address.strip(), consent_status,
    )
    log_action("Created organ donor", "organ_donors",
               f"Donor: {name.strip()} (Organ: {organ_type})")
    return True, f"Organ donor added successfully (ID: {donor_id})"


def edit_organ_donor(donor_id, name, age, gender, blood_group, organ_type,
                     phone="", email="", address="", consent_status="Pending",
                     status="Available"):
    """Validate and update an organ donor."""
    validations = [
        validate_name(name),
        validate_age(str(age)),
        validate_gender(gender),
        validate_blood_group(blood_group),
        validate_organ_type(organ_type),
        validate_phone(phone),
        validate_email(email),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    success = update_organ_donor(
        donor_id, name.strip(), int(age), gender, blood_group, organ_type,
        phone.strip(), email.strip(), address.strip(), consent_status, status,
    )
    if success:
        log_action("Updated organ donor", "organ_donors",
                   f"Donor ID: {donor_id}")
    return success, "Organ donor updated successfully" if success else "Failed to update donor"


def remove_organ_donor(donor_id):
    """Delete an organ donor."""
    success = delete_organ_donor(donor_id)
    if success:
        log_action("Deleted organ donor", "organ_donors",
                   f"Donor ID: {donor_id}")
    return success


def change_consent(donor_id, consent_status):
    """Update the consent status of an organ donor."""
    success = update_consent_status(donor_id, consent_status)
    if success:
        log_action("Updated consent status", "organ_donors",
                   f"Donor ID: {donor_id}, Status: {consent_status}")
    return success


def list_organ_donors(name="", organ_type="", blood_group=""):
    """List organ donors with optional search filters."""
    if name or (organ_type and organ_type != "All") or (blood_group and blood_group != "All"):
        return search_organ_donors(name, organ_type, blood_group)
    return get_all_organ_donors()
