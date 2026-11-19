"""Tests for atomic blood inventory and request fulfillment."""

import os
import tempfile
import unittest

import config

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from database import initialize_db
from database.connection import get_connection
from models.blood_request_model import (
    add_blood_request,
    get_blood_request_by_id,
)
from models.inventory_model import get_inventory_by_blood_group, increment_units
from services.blood_request_service import change_blood_request_status


class TestBloodRequestAtomicity(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(dir=os.path.join(_project_root, "tests"))
        config.get_app_data_dir = lambda: self.temp_dir
        initialize_db()

    def test_fulfillment_updates_request_and_inventory_together(self):
        request_id = add_blood_request("Patient One", "A+", 2)
        increment_units("A+", 2)

        success, _ = change_blood_request_status(request_id, "Fulfilled")

        self.assertTrue(success)
        self.assertEqual(get_blood_request_by_id(request_id)["status"], "Fulfilled")
        self.assertEqual(
            get_inventory_by_blood_group("A+")["units_available"], 0
        )

    def test_request_update_failure_rolls_back_inventory_deduction(self):
        request_id = add_blood_request("Patient Two", "B+", 1)
        increment_units("B+", 1)
        conn = get_connection()
        conn.execute(
            """CREATE TRIGGER fail_blood_fulfillment
               BEFORE UPDATE OF status ON blood_requests
               WHEN NEW.status = 'Fulfilled'
               BEGIN
                   SELECT RAISE(ABORT, 'forced request update failure');
               END"""
        )
        conn.commit()
        conn.close()

        success, message = change_blood_request_status(request_id, "Fulfilled")

        cleanup = get_connection()
        cleanup.execute("DROP TRIGGER fail_blood_fulfillment")
        cleanup.commit()
        cleanup.close()

        self.assertFalse(success)
        self.assertIn("forced request update failure", message)
        self.assertEqual(get_blood_request_by_id(request_id)["status"], "Pending")
        self.assertEqual(
            get_inventory_by_blood_group("B+")["units_available"], 1
        )


if __name__ == "__main__":
    unittest.main()
