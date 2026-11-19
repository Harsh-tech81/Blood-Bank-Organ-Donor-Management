"""
Organ request service — business logic for organ requests.
Ensures clinical integrity: checks for active consented donors before matching
or fulfilling, and manages donor lifecycle status.
"""

from models.organ_request_model import (
    add_organ_request, get_all_organ_requests,
    delete_organ_request, search_organ_requests, get_pending_organ_requests_count,
    get_organ_request_by_id, transition_organ_request_status,
)
from models.organ_donor_model import search_organ_donors
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
    - Matching reserves an eligible donor against this request.
    - Fulfilling verifies that reservation and marks the donor as 'Donated'.
    """
    req = get_organ_request_by_id(request_id)
    current_status = req["status"] if req else None
    success, error, donor = transition_organ_request_status(request_id, new_status)
    if success:
        if donor and new_status == "Matched":
            log_action("Reserved organ donor", "organ_donors",
                       f"Donor #{donor['id']} ({donor['name']}) reserved for Request #{request_id}")
        elif donor and new_status == "Fulfilled":
            log_action("Allocated organ donor", "organ_donors",
                       f"Donor #{donor['id']} ({donor['name']}) allocated to Request #{request_id}")
        log_action("Updated organ request status", "organ_requests",
                   f"Request #{request_id} changed from {current_status} to {new_status}")
        return True, f"Organ request #{request_id} status updated to '{new_status}'."
    return False, error


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
