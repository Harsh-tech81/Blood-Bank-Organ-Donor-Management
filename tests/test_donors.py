"""
Unit tests for blood donor and inventory models.
Tests run against a temporary in-memory or temp-file database.
"""

import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override the DB path to use a temp directory for testing
import config
_temp_dir = tempfile.mkdtemp(dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
config.get_app_data_dir = lambda: _temp_dir

from database import initialize_db
from models.donor_model import (
    add_donor, get_all_donors, get_donor_by_id,
    update_donor, delete_donor, search_donors,
    record_donation, get_donation_history, get_donor_count,
)
from models.inventory_model import (
    get_all_inventory, increment_units, decrement_units,
    get_total_blood_units,
)


class TestDonorModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize the database once for all tests."""
        initialize_db()

    def test_add_and_get_donor(self):
        """Adding a donor should make it retrievable."""
        donor_id = add_donor("Test User", 25, "Male", "A+", "9999999999", "test@test.com", "123 Street")
        self.assertIsNotNone(donor_id)

        donor = get_donor_by_id(donor_id)
        self.assertIsNotNone(donor)
        self.assertEqual(donor["name"], "Test User")
        self.assertEqual(donor["blood_group"], "A+")

    def test_get_all_donors(self):
        """get_all_donors should return a list."""
        donors = get_all_donors()
        self.assertIsInstance(donors, list)

    def test_update_donor(self):
        """Updating a donor should change its data."""
        donor_id = add_donor("Update Me", 30, "Female", "B-", "", "", "")
        success = update_donor(donor_id, "Updated Name", 31, "Female", "B+", "", "", "")
        self.assertTrue(success)

        donor = get_donor_by_id(donor_id)
        self.assertEqual(donor["name"], "Updated Name")
        self.assertEqual(donor["blood_group"], "B+")

    def test_delete_donor(self):
        """Deleting a donor should remove it."""
        donor_id = add_donor("Delete Me", 22, "Male", "O+", "", "", "")
        success = delete_donor(donor_id)
        self.assertTrue(success)

        donor = get_donor_by_id(donor_id)
        self.assertIsNone(donor)

    def test_search_donors_by_name(self):
        """Search should find donors by partial name match."""
        add_donor("Rahul Sharma", 28, "Male", "AB+", "", "", "")
        results = search_donors(name="Rahul")
        self.assertTrue(any(d["name"] == "Rahul Sharma" for d in results))

    def test_search_donors_by_blood_group(self):
        """Search should filter by blood group."""
        add_donor("Blood Test", 25, "Male", "O-", "", "", "")
        results = search_donors(blood_group="O-")
        self.assertTrue(all(d["blood_group"] == "O-" for d in results))

    def test_donor_count(self):
        """Donor count should be non-negative."""
        count = get_donor_count()
        self.assertGreaterEqual(count, 0)


class TestDonationModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        initialize_db()

    def test_record_and_get_history(self):
        """Recording a donation should appear in history."""
        donor_id = add_donor("Donor History", 30, "Male", "A+", "", "", "")
        donation_id = record_donation(donor_id, units=2, notes="Test donation")
        self.assertIsNotNone(donation_id)

        history = get_donation_history(donor_id)
        self.assertTrue(len(history) >= 1)
        self.assertEqual(history[0]["units"], 2)


class TestInventoryModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        initialize_db()

    def test_all_blood_groups_exist(self):
        """All 8 blood groups should be in inventory."""
        inventory = get_all_inventory()
        groups = [item["blood_group"] for item in inventory]
        for bg in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            self.assertIn(bg, groups)

    def test_increment_units(self):
        """Incrementing should increase stock."""
        initial = get_total_blood_units()
        increment_units("A+", 5)
        after = get_total_blood_units()
        self.assertEqual(after, initial + 5)

    def test_decrement_units(self):
        """Decrementing should decrease stock (if available)."""
        increment_units("B+", 10)
        success = decrement_units("B+", 3)
        self.assertTrue(success)

    def test_decrement_below_zero_fails(self):
        """Cannot decrement more than available."""
        success = decrement_units("AB-", 9999)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
