"""
Unit tests for authentication service.
"""

import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import hash_password, verify_password


class TestAuthService(unittest.TestCase):
    """Test cases for auth_service."""

    def test_hash_password_returns_string(self):
        """hash_password should return a non-empty string."""
        hashed = hash_password("testpassword")
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)

    def test_hash_password_different_each_time(self):
        """Two hashes of the same password should differ (different salts)."""
        hash1 = hash_password("testpassword")
        hash2 = hash_password("testpassword")
        self.assertNotEqual(hash1, hash2)

    def test_verify_correct_password(self):
        """verify_password should return True for the correct password."""
        password = "mySecureP@ss"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))

    def test_verify_wrong_password(self):
        """verify_password should return False for a wrong password."""
        hashed = hash_password("correct_password")
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_verify_empty_password(self):
        """verify_password should handle empty password correctly."""
        hashed = hash_password("")
        self.assertTrue(verify_password("", hashed))
        self.assertFalse(verify_password("not_empty", hashed))


if __name__ == "__main__":
    unittest.main()
