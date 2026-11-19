"""
Organ request service — business logic for organ requests.
Ensures clinical integrity: checks for active consented donors before matching
or fulfilling, and manages donor lifecycle status.
"""

from models.organ_request_model import (
    add_organ_request, get_all_organ_requests, update_organ_request_status,
    delete_organ_request, search_organ_requests, get_pending_organ_requests_count,
    get_organ_request_by_id,
)
from models.organ_donor_model import search_organ_donors, update_organ_donor
from models.activity_log_model import log_action
from utils.validators import validate_name, validate_organ_type


def create_organ_request(patient_name, organ_type, blood_group="",
                         hospital="", urgency="Normal"):
    """
    Validate and register an organ recipient requisition.
    Can be placed at any time; system will check if compatible consented donors exist.
    """
    validations = [
        validate_name(patient_name),
        validate_organ_type(organ_type),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    request_id = add_organ_request(
        patient_name.strip(), organ_type, blood_group,
        hospital.strip(), urgency,
    )

    # Check if there is an eligible consented donor available
    matches = search_organ_donors(organ_type=organ_type, blood_group=blood_group if blood_group else "All")
    consented_available = [
        d for d in matches
        if d.get("consent_status") == "Consented" and d.get("status") == "Available"
    ]

    match_msg = ""
    if consented_available:
        match_msg = f" (Found {len(consented_available)} eligible consented donor(s) in registry)."
    else:
        match_msg = " (No consented donor currently matched. Request logged in waiting list)."

    log_action("Created organ request", "organ_requests",
               f"Patient: {patient_name.strip()}, Organ: {organ_type}, Urgency: {urgency}")
    return True, f"Organ request registered (ID: {request_id}).{match_msg}"


def change_organ_request_status(request_id, new_status):
    """
    Update organ request status with donor matching safeguards.
    - Matching / Fulfilling verifies that an eligible donor exists.
    - Fulfilling reserves and marks the donor as 'Donated'.
    """
    req = get_organ_request_by_id(request_id)
    if not req:
        return False, "Organ request record not found."

    organ_type = req["organ_type"]
    blood_group = req["blood_group"]
    current_status = req["status"]

    if new_status in ["Matched", "Fulfilled"] and current_status == "Pending":
        # Check for consented available donor
        candidates = search_organ_donors(organ_type=organ_type, blood_group=blood_group if blood_group else "All")
        eligible = [
            d for d in candidates
            if d.get("consent_status") == "Consented" and d.get("status") == "Available"
        ]

        if not eligible:
            return False, f"Cannot set to '{new_status}': No active, legally consented donor found for {organ_type} (Blood: {blood_group or 'Any'})."

        # If fulfilling, transition one matching donor to 'Donated'
        if new_status == "Fulfilled":
            donor_to_allocate = eligible[0]
            update_organ_donor(
                donor_id=donor_to_allocate["id"],
                name=donor_to_allocate["name"],
                age=donor_to_allocate["age"],
                gender=donor_to_allocate["gender"],
                blood_group=donor_to_allocate["blood_group"],
                organ_type=donor_to_allocate["organ_type"],
                phone=donor_to_allocate.get("phone", ""),
                email=donor_to_allocate.get("email", ""),
                address=donor_to_allocate.get("address", ""),
                consent_status=donor_to_allocate.get("consent_status", "Consented"),
                status="Donated",
            )
            log_action("Allocated organ donor", "organ_donors",
                       f"Donor #{donor_to_allocate['id']} ({donor_to_allocate['name']}) allocated to Request #{request_id}")

    success = update_organ_request_status(request_id, new_status)
    if success:
        log_action("Updated organ request status", "organ_requests",
                   f"Request #{request_id} changed from {current_status} to {new_status}")
        return True, f"Organ request #{request_id} status updated to '{new_status}'."
    return False, "Failed to update organ request status."


def remove_organ_request(request_id):
    """Delete an organ request."""
    success = delete_organ_request(request_id)
    if success:
        log_action("Deleted organ request", "organ_requests",
                   f"Request ID: {request_id}")
    return success


def list_organ_requests(patient_name="", organ_type="", status=""):
    """List organ requests ordered by clinical urgency."""
    if patient_name or (organ_type and organ_type != "All") or (status and status != "All"):
        return search_organ_requests(patient_name, organ_type, status)
    return get_all_organ_requests()


def get_pending_count():
    """Get count of pending organ requests."""
    return get_pending_organ_requests_count()
