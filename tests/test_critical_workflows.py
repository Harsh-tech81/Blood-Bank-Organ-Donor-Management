"""Integration tests for the critical business workflows."""

import os
import tempfile
import unittest

import config
from database import initialize_db
from database.connection import get_connection
from models.blood_request_model import get_blood_request_by_id
from models.donor_model import add_donor, get_donor_by_id
from models.inventory_model import get_inventory_by_blood_group
from models.organ_donor_model import (
    add_organ_donor,
    get_organ_donor_by_id,
)
from models.organ_request_model import get_organ_request_by_id
from services.auth_service import login, logout, register_user
from services.blood_request_service import (
    change_blood_request_status,
    create_blood_request,
)
from services.organ_request_service import (
    authorize_transplant,
    change_organ_request_status,
    create_organ_request,
    propose_allocation,
    review_request,
)
from services.organ_service import change_consent, review_donor


class TestCriticalWorkflows(unittest.TestCase):
    """Verify safeguards across the service and persistence boundaries."""

    def setUp(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.temp_dir = tempfile.mkdtemp(dir=os.path.join(project_root, "tests"))
        config.get_app_data_dir = lambda: self.temp_dir
        logout()
        initialize_db()

    def tearDown(self):
        logout()

    def test_insufficient_blood_stock_keeps_request_pending(self):
        created, message = create_blood_request("Shortage Patient", "A+", 2)
        self.assertTrue(created, message)

        request = get_blood_request_by_id(1)
        success, error = change_blood_request_status(request["id"], "Fulfilled")

        self.assertFalse(success)
        self.assertIn("Only 0 unit(s)", error)
        self.assertEqual(get_blood_request_by_id(request["id"])["status"], "Pending")
        self.assertEqual(
            get_inventory_by_blood_group("A+")["units_available"],
            0,
        )

    def test_withdrawn_consent_blocks_existing_allocation_proposal(self):
        login("admin", "admin123")
        donor_id, request_id = self._prepare_organ_allocation()

        self.assertTrue(change_consent(donor_id, "Withdrawn"))
        success, error = change_organ_request_status(request_id, "Matched")

        self.assertFalse(success)
        self.assertIn("consent", error)
        self.assertEqual(get_organ_request_by_id(request_id)["status"], "Pending")
        self.assertEqual(get_organ_donor_by_id(donor_id)["status"], "Available")

    def test_one_donor_cannot_be_allocated_to_two_requests(self):
        login("admin", "admin123")
        donor_id, first_request_id = self._prepare_organ_allocation()
        self.assertTrue(change_organ_request_status(first_request_id, "Matched")[0])

        second_created, message = create_organ_request(
            "Second Recipient", "Kidney", "A+"
        )
        self.assertTrue(second_created, message)
        second_request_id = 2
        self.assertTrue(
            review_request(second_request_id, "Approved", "Second request reviewed.")[0]
        )

        proposed, error = propose_allocation(second_request_id)

        self.assertFalse(proposed)
        self.assertIn("No donor", error)
        self.assertEqual(
            get_organ_request_by_id(first_request_id)["matched_donor_id"],
            donor_id,
        )
        self.assertIsNone(get_organ_request_by_id(second_request_id)["matched_donor_id"])

    def test_unauthorized_account_cannot_register_administrator(self):
        self.assertTrue(login("staff", "staff123")[0])

        success, message = register_user(
            "unauthorized-admin", "secure-password", "Administrator"
        )

        self.assertFalse(success)
        self.assertIn("Only administrators", message)

    def test_invalid_blood_group_and_negative_quantity_are_rejected(self):
        invalid_group, group_message = create_blood_request(
            "Invalid Group Patient", "X+", 1
        )
        negative_quantity, quantity_message = create_blood_request(
            "Negative Quantity Patient", "A+", -1
        )

        self.assertFalse(invalid_group)
        self.assertIn("blood group", group_message.lower())
        self.assertFalse(negative_quantity)
        self.assertIn("at least 1", quantity_message.lower())

    def test_data_persists_after_database_reinitialization(self):
        donor_id = add_donor(
            "Persistent Donor", 30, "Other", "O+", "", "", ""
        )
        created, message = create_blood_request("Persistent Patient", "O+", 1)
        self.assertTrue(created, message)

        initialize_db()

        self.assertEqual(get_donor_by_id(donor_id)["name"], "Persistent Donor")
        persisted_request = get_blood_request_by_id(1)
        self.assertEqual(persisted_request["patient_name"], "Persistent Patient")
        self.assertEqual(persisted_request["blood_group"], "O+")

    def _prepare_organ_allocation(self):
        donor_id = add_organ_donor(
            "Consent Donor", 30, "Male", "A+", "Kidney",
            consent_status="Consented",
        )
        request_id = 1
        created, message = create_organ_request(
            "Organ Recipient", "Kidney", "A+"
        )
        self.assertTrue(created, message)
        self.assertTrue(review_donor(
            donor_id, "Verified", "Registry documents reviewed."
        )[0])
        self.assertTrue(review_request(
            request_id, "Approved", "Recipient request reviewed."
        )[0])
        self.assertTrue(propose_allocation(request_id)[0])
        self.assertTrue(authorize_transplant(
            request_id,
            donor_id,
            "Academic Transplant Authority",
            "AUTH-CRITICAL",
            "External authorization recorded for testing.",
        )[0])
        return donor_id, request_id


if __name__ == "__main__":
    unittest.main()
