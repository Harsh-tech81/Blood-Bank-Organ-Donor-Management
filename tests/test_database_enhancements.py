"""Regression tests for normalized records, batches, and allocation history."""

import os
import tempfile
import unittest

import config
from database import initialize_db
from database.connection import get_connection
from models.donor_model import add_donor, record_donation_with_batch
from models.blood_request_model import add_blood_request, fulfill_blood_request
from models.organ_donor_model import add_organ_donor
from models.organ_request_model import add_organ_request
from models.organ_allocation_model import get_all_allocations
from services.organ_request_service import change_organ_request_status


class TestDatabaseEnhancements(unittest.TestCase):
    def setUp(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.temp_dir = tempfile.mkdtemp(dir=os.path.join(project_root, "tests"))
        config.get_app_data_dir = lambda: self.temp_dir
        initialize_db()

    def test_request_creates_reusable_recipient_and_hospital_references(self):
        first_id = add_blood_request(
            "Normalized Patient", "A+", 1, "City Hospital"
        )
        second_id = add_organ_request(
            "Normalized Patient", "Kidney", "A+", "city hospital"
        )
        conn = get_connection()
        first = conn.execute(
            "SELECT recipient_id, hospital_id FROM blood_requests WHERE id = ?",
            (first_id,),
        ).fetchone()
        second = conn.execute(
            "SELECT recipient_id, hospital_id FROM organ_requests WHERE id = ?",
            (second_id,),
        ).fetchone()
        counts = conn.execute(
            "SELECT (SELECT COUNT(*) FROM recipients), (SELECT COUNT(*) FROM hospitals)"
        ).fetchone()
        conn.close()
        self.assertEqual(first["recipient_id"], second["recipient_id"])
        self.assertEqual(first["hospital_id"], second["hospital_id"])
        self.assertEqual(tuple(counts), (1, 1))

    def test_donation_creates_expiring_batch_and_fulfillment_consumes_it(self):
        donor_id = add_donor("Batch Donor", 30, "Other", "O+", "", "", "")
        record_donation_with_batch(donor_id, "O+", 2)
        request_id = add_blood_request("Batch Patient", "O+", 1)

        success, message = fulfill_blood_request(request_id)

        self.assertTrue(success, message)
        conn = get_connection()
        batch = conn.execute(
            "SELECT units_received, units_remaining, status FROM blood_inventory_batches"
        ).fetchone()
        conn.close()
        self.assertEqual(tuple(batch), (2, 1, "Available"))

    def test_organ_allocation_history_tracks_fulfillment(self):
        donor_id = add_organ_donor(
            "Allocation Donor", 40, "Female", "A+", "Kidney",
            consent_status="Consented",
        )
        request_id = add_organ_request(
            "Allocation Recipient", "Kidney", "A+", "Regional Hospital"
        )
        self.assertTrue(change_organ_request_status(request_id, "Matched")[0])
        self.assertTrue(change_organ_request_status(request_id, "Fulfilled")[0])

        allocations = get_all_allocations()

        self.assertEqual(len(allocations), 1)
        self.assertEqual(allocations[0]["donor_id"], donor_id)
        self.assertEqual(allocations[0]["organ_request_id"], request_id)
        self.assertEqual(allocations[0]["status"], "Fulfilled")
        self.assertEqual(allocations[0]["recipient_name"], "Allocation Recipient")


if __name__ == "__main__":
    unittest.main()
