"""Tests for role authorization during account registration."""

import unittest
from unittest.mock import patch

import services.auth_service as auth_service


class TestAuthRegistration(unittest.TestCase):

    def tearDown(self):
        auth_service.logout()

    @patch("services.auth_service.get_user_by_username", return_value=None)
    @patch("models.user_model.create_user")
    def test_public_registration_can_only_create_staff(self, create_user, _get_user):
        success, message = auth_service.register_user(
            "new-admin", "secure-password", "Administrator"
        )

        self.assertFalse(success)
        self.assertIn("Only administrators", message)
        create_user.assert_not_called()

    @patch("services.auth_service.get_user_by_username", return_value=None)
    @patch("models.user_model.create_user")
    def test_staff_cannot_create_privileged_account(self, create_user, _get_user):
        auth_service._current_user = {"username": "staff", "role": "Medical Staff"}

        success, message = auth_service.register_user(
            "promoted-user", "secure-password", "Medical Officer"
        )

        self.assertFalse(success)
        self.assertIn("Only administrators", message)
        create_user.assert_not_called()

    @patch("services.auth_service.get_user_by_username", return_value=None)
    @patch("models.user_model.create_user", return_value=1)
    def test_administrator_can_create_privileged_account(self, create_user, _get_user):
        auth_service._current_user = {"username": "admin", "role": "Administrator"}

        success, _ = auth_service.register_user(
            "new-officer", "secure-password", "Medical Officer"
        )

        self.assertTrue(success)
        create_user.assert_called_once()
        self.assertEqual(create_user.call_args.args[2], "Medical Officer")

    @patch("services.auth_service.get_user_by_username", return_value=None)
    @patch("models.user_model.create_user", return_value=1)
    def test_public_registration_creates_staff_account(self, create_user, _get_user):
        success, _ = auth_service.register_user(
            "new-staff", "secure-password", "Staff Member"
        )

        self.assertTrue(success)
        self.assertEqual(create_user.call_args.args[2], "Staff Member")


if __name__ == "__main__":
    unittest.main()
