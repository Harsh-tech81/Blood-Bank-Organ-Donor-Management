"""
Blood inventory service — business logic for stock management.
"""

from models.inventory_model import (
    get_all_inventory, get_inventory_by_blood_group,
    update_stock, increment_units, decrement_units, get_total_blood_units,
)
from models.activity_log_model import log_action


def get_inventory():
    """Get all blood inventory."""
    return get_all_inventory()


def add_blood_units(blood_group, units):
    """Add units to a blood group's stock."""
    success = increment_units(blood_group, units)
    if success:
        log_action("Added blood units", "blood_inventory",
                   f"Group: {blood_group}, Units: +{units}")
    return success


def remove_blood_units(blood_group, units):
    """Remove units from a blood group's stock."""
    success = decrement_units(blood_group, units)
    if success:
        log_action("Removed blood units", "blood_inventory",
                   f"Group: {blood_group}, Units: -{units}")
    return success, "" if success else "Not enough units in stock"


def set_blood_units(blood_group, units):
    """Set exact units for a blood group."""
    success = update_stock(blood_group, units)
    if success:
        log_action("Set blood units", "blood_inventory",
                   f"Group: {blood_group}, Units: {units}")
    return success


def get_total_units():
    """Get total blood units across all groups."""
    return get_total_blood_units()
