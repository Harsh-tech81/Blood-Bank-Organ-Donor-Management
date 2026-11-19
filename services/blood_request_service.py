"""
Blood request service — business logic for blood requests.
"""

from models.blood_request_model import (
    add_blood_request, get_all_blood_requests, update_blood_request_status,
    delete_blood_request, search_blood_requests, get_pending_blood_requests_count,
)
from models.activity_log_model import log_action
from utils.validators import validate_name, validate_blood_group, validate_positive_integer


def create_blood_request(patient_name, blood_group, units_needed=1,
                         hospital="", urgency="Normal"):
    """Validate and create a new blood request."""
    validations = [
        validate_name(patient_name),
        validate_blood_group(blood_group),
        validate_positive_integer(str(units_needed), "Units needed"),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    request_id = add_blood_request(
        patient_name.strip(), blood_group, int(units_needed),
        hospital.strip(), urgency,
    )
    log_action("Created blood request", "blood_requests",
               f"Patient: {patient_name.strip()}, Group: {blood_group}")
    return True, f"Blood request created (ID: {request_id})"


def change_blood_request_status(request_id, status):
    """Update blood request status."""
    success = update_blood_request_status(request_id, status)
    if success:
        log_action("Updated blood request status", "blood_requests",
                   f"Request ID: {request_id}, Status: {status}")
    return success


def remove_blood_request(request_id):
    """Delete a blood request."""
    success = delete_blood_request(request_id)
    if success:
        log_action("Deleted blood request", "blood_requests",
                   f"Request ID: {request_id}")
    return success


def list_blood_requests(patient_name="", blood_group="", status=""):
    """List blood requests with optional filters."""
    if patient_name or (blood_group and blood_group != "All") or (status and status != "All"):
        return search_blood_requests(patient_name, blood_group, status)
    return get_all_blood_requests()


def get_pending_count():
    """Get count of pending blood requests."""
    return get_pending_blood_requests_count()
