"""Tests for atomic organ request matching and fulfillment."""

import os
import tempfile
import unittest

import config

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from database import initialize_db
from services.auth_service import login
from models.organ_donor_model import add_organ_donor, get_organ_donor_by_id
from models.organ_request_model import (
    add_organ_request,
    delete_organ_request,
    get_organ_request_by_id,
)
from services.organ_request_service import change_organ_request_status
from services.organ_request_service import (
    review_request, propose_allocation, authorize_transplant,
)
from services.organ_service import review_donor


class TestOrganRequestAllocation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(dir=os.path.join(_project_root, "tests"))
        config.get_app_data_dir = lambda: self.temp_dir
        initialize_db()
        login("admin", "admin123")

    def _create_request_and_donor(self):
        donor_id = add_organ_donor(
            "Donor One", 30, "Male", "A+", "Kidney",
            consent_status="Consented",
        )
        request_id = add_organ_request("Patient One", "Kidney", "A+")
        self.assertTrue(review_donor(donor_id, "Verified", "Registry documents reviewed.")[0])
        self.assertTrue(review_request(request_id, "Approved", "Recipient request reviewed.")[0])
        self.assertTrue(propose_allocation(request_id)[0])
        self.assertTrue(authorize_transplant(
            request_id, donor_id, "Academic Transplant Authority",
            "AUTH-TEST", "External authorization recorded for demonstration.",
        )[0])
        return request_id, donor_id

    def test_matching_reserves_donor_and_persists_match(self):
        request_id, donor_id = self._create_request_and_donor()

        success, _ = change_organ_request_status(request_id, "Matched")

        self.assertTrue(success)
        request = get_organ_request_by_id(request_id)
        donor = get_organ_donor_by_id(donor_id)
        self.assertEqual(request["status"], "Matched")
        self.assertEqual(request["matched_donor_id"], donor_id)
        self.assertEqual(donor["status"], "Matched")

    def test_fulfillment_requires_and_consumes_reservation(self):
        request_id, donor_id = self._create_request_and_donor()
        change_organ_request_status(request_id, "Matched")

        success, _ = change_organ_request_status(request_id, "Fulfilled")

        self.assertTrue(success)
        self.assertEqual(get_organ_request_by_id(request_id)["status"], "Fulfilled")
        self.assertEqual(get_organ_donor_by_id(donor_id)["status"], "Donated")

    def test_pending_request_cannot_be_fulfilled_directly(self):
        donor_id = add_organ_donor(
            "Donor Pending", 30, "Male", "A+", "Kidney",
            consent_status="Consented",
        )
        request_id = add_organ_request("Patient Pending", "Kidney", "A+")

        success, message = change_organ_request_status(request_id, "Fulfilled")

        self.assertFalse(success)
        self.assertIn("verified matched donor reservation", message)
        self.assertEqual(get_organ_request_by_id(request_id)["status"], "Pending")
        self.assertEqual(get_organ_donor_by_id(donor_id)["status"], "Available")

    def test_proposal_requires_request_review(self):
        donor_id = add_organ_donor(
            "Donor Unreviewed Request", 30, "Male", "A+", "Kidney",
            consent_status="Consented",
        )
        review_donor(donor_id, "Verified", "Registry documents reviewed.")
        request_id = add_organ_request("Patient Unreviewed", "Kidney", "A+")

        success, message = propose_allocation(request_id)

        self.assertFalse(success)
        self.assertIn("recipient/request review", message)

    def test_authority_approval_is_required_before_reservation(self):
        donor_id = add_organ_donor(
            "Donor Without Authority", 30, "Male", "A+", "Kidney",
            consent_status="Consented",
        )
        request_id = add_organ_request("Patient Without Authority", "Kidney", "A+")
        review_donor(donor_id, "Verified", "Registry documents reviewed.")
        review_request(request_id, "Approved", "Recipient request reviewed.")
        propose_allocation(request_id)

        success, message = change_organ_request_status(request_id, "Matched")

        self.assertFalse(success)
        self.assertIn("transplant-authority authorization", message)
        self.assertEqual(get_organ_donor_by_id(donor_id)["status"], "Available")

    def test_deleting_matched_request_releases_donor(self):
        request_id, donor_id = self._create_request_and_donor()
        change_organ_request_status(request_id, "Matched")

        self.assertTrue(delete_organ_request(request_id))
        self.assertIsNone(get_organ_request_by_id(request_id))
        self.assertEqual(get_organ_donor_by_id(donor_id)["status"], "Available")


if __name__ == "__main__":
    unittest.main()
