"""Tests for activity log user attribution."""

import unittest
from unittest.mock import patch

from models.activity_log_model import log_action


class TestActivityLog(unittest.TestCase):

    @patch("models.activity_log_model.get_current_user")
    @patch("models.activity_log_model.get_current_timestamp", return_value="timestamp")
    @patch("models.activity_log_model.get_connection")
    def test_log_action_uses_active_username(
        self, get_connection, _get_timestamp, get_current_user
    ):
        cursor = get_connection.return_value.cursor.return_value
        get_current_user.return_value = {"username": "staff"}

        log_action("Created donor", "blood_donors", "Donor #1")

        params = cursor.execute.call_args.args[1]
        self.assertEqual(params[3], "staff")
        get_connection.return_value.commit.assert_called_once()
        get_connection.return_value.close.assert_called_once()

    @patch("models.activity_log_model.get_current_user", return_value=None)
    @patch("models.activity_log_model.get_current_timestamp", return_value="timestamp")
    @patch("models.activity_log_model.get_connection")
    def test_log_action_uses_system_for_missing_session(
        self, get_connection, _get_timestamp, _get_current_user
    ):
        cursor = get_connection.return_value.cursor.return_value

        log_action("Scheduled cleanup", "system")

        params = cursor.execute.call_args.args[1]
        self.assertEqual(params[3], "system")

    @patch("models.activity_log_model.get_current_user", return_value={"username": "staff"})
    @patch("models.activity_log_model.get_current_timestamp", return_value="timestamp")
    @patch("models.activity_log_model.get_connection")
    def test_explicit_actor_is_preserved(
        self, get_connection, _get_timestamp, _get_current_user
    ):
        cursor = get_connection.return_value.cursor.return_value

        log_action("Imported data", "reports", performed_by="migration")

        params = cursor.execute.call_args.args[1]
        self.assertEqual(params[3], "migration")


if __name__ == "__main__":
    unittest.main()
