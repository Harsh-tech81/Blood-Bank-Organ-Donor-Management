"""
Blood request service — business logic for blood requests.
Ensures clinical integrity: checks stock reserves before approving or fulfilling,
automatically deducts blood inventory upon fulfillment, and updates activity logs.
"""

from models.blood_request_model import (
    add_blood_request, get_all_blood_requests, update_blood_request_status,
    delete_blood_request, search_blood_requests, get_pending_blood_requests_count,
    get_blood_request_by_id,
)
from models.inventory_model import get_inventory_by_blood_group, decrement_units
from models.activity_log_model import log_action
from utils.validators import validate_name, validate_blood_group, validate_positive_integer


def create_blood_request(patient_name, blood_group, units_needed=1,
                         hospital="", urgency="Normal"):
    """
    Validate and record a new blood request.
    Patients can always register demands (even during shortages) so the
    hospital has visibility of active deficits.
    """
    validations = [
        validate_name(patient_name),
        validate_blood_group(blood_group),
        validate_positive_integer(str(units_needed), "Units needed"),
    ]
    for valid, msg in validations:
        if not valid:
            return False, msg

    units = int(units_needed)
    request_id = add_blood_request(
        patient_name.strip(), blood_group, units,
        hospital.strip(), urgency,
    )

    # Check immediate stock availability to inform the staff
    stock_record = get_inventory_by_blood_group(blood_group)
    available = stock_record["units_available"] if stock_record else 0

    stock_msg = ""
    if available < units:
        deficit = units - available
        stock_msg = f" ⚠️ Note: Stock deficit ({available}/{units} units currently on hand)."
    else:
        stock_msg = f" (In stock: {available} units available)."

    log_action("Created blood request", "blood_requests",
               f"Patient: {patient_name.strip()}, Group: {blood_group}, Urgency: {urgency}, Units: {units}")
    return True, f"Blood request registered (ID: {request_id}).{stock_msg}"


def change_blood_request_status(request_id, new_status):
    """
    Update blood request status with inventory safety checks.
    - Fulfilling deducts the requested units from the inventory.
    - Prevents fulfillment if stock is insufficient.
    """
    req = get_blood_request_by_id(request_id)
    if not req:
        return False, "Request record not found."

    current_status = req["status"]
    blood_group = req["blood_group"]
    units = req["units_needed"]

    if new_status == "Fulfilled" and current_status != "Fulfilled":
        # Check stock before deducting
        stock_record = get_inventory_by_blood_group(blood_group)
        available = stock_record["units_available"] if stock_record else 0
        if available < units:
            return False, f"Cannot fulfill request: Only {available} unit(s) of {blood_group} available in inventory (Need {units})."

        # Decrement stock
        deducted = decrement_units(blood_group, units)
        if not deducted:
            return False, "Failed to deduct units from blood inventory."

        log_action("Inventory deducted on fulfillment", "blood_inventory",
                   f"Deducted {units} unit(s) of {blood_group} for Request #{request_id}")

    success = update_blood_request_status(request_id, new_status)
    if success:
        log_action("Updated blood request status", "blood_requests",
                   f"Request #{request_id} status changed from {current_status} to {new_status}")
        return True, f"Request #{request_id} updated to '{new_status}' successfully."
    return False, "Database update failed."


def remove_blood_request(request_id):
    """Delete a blood request."""
    success = delete_blood_request(request_id)
    if success:
        log_action("Deleted blood request", "blood_requests",
                   f"Request ID: {request_id}")
    return success


def list_blood_requests(patient_name="", blood_group="", status=""):
    """List blood requests ordered by urgency (Critical -> Urgent -> Normal)."""
    if patient_name or (blood_group and blood_group != "All") or (status and status != "All"):
        return search_blood_requests(patient_name, blood_group, status)
    return get_all_blood_requests()


def get_pending_count():
    """Get count of pending blood requests."""
    return get_pending_blood_requests_count()
