"""
Organ request service — business logic for organ requests.
"""

from models.organ_request_model import (
    add_organ_request, get_all_organ_requests, update_organ_request_status,
    delete_organ_request, search_organ_requests, get_pending_organ_requests_count,
)
from models.activity_log_model import log_action
from utils.validators import validate_name, validate_organ_type


def create_organ_request(patient_name, organ_type, blood_group="",
                         hospital="", urgency="Normal"):
    """Validate and create a new organ request."""
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
    log_action("Created organ request", "organ_requests",
               f"Patient: {patient_name.strip()}, Organ: {organ_type}")
    return True, f"Organ request created (ID: {request_id})"


def change_organ_request_status(request_id, status):
    """Update organ request status."""
    success = update_organ_request_status(request_id, status)
    if success:
        log_action("Updated organ request status", "organ_requests",
                   f"Request ID: {request_id}, Status: {status}")
    return success


def remove_organ_request(request_id):
    """Delete an organ request."""
    success = delete_organ_request(request_id)
    if success:
        log_action("Deleted organ request", "organ_requests",
                   f"Request ID: {request_id}")
    return success


def list_organ_requests(patient_name="", organ_type="", status=""):
    """List organ requests with optional filters."""
    if patient_name or (organ_type and organ_type != "All") or (status and status != "All"):
        return search_organ_requests(patient_name, organ_type, status)
    return get_all_organ_requests()


def get_pending_count():
    """Get count of pending organ requests."""
    return get_pending_organ_requests_count()
