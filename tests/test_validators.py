"""
Unit tests for input validators.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import (
    validate_name, validate_age, validate_donor_age,
    validate_phone, validate_email, validate_blood_group,
    validate_gender, validate_organ_type, validate_required,
    validate_positive_integer,
)


class TestValidateName(unittest.TestCase):

    def test_valid_name(self):
        valid, _ = validate_name("John Doe")
        self.assertTrue(valid)

    def test_empty_name(self):
        valid, msg = validate_name("")
        self.assertFalse(valid)
        self.assertIn("required", msg.lower())

    def test_short_name(self):
        valid, _ = validate_name("A")
        self.assertFalse(valid)

    def test_name_with_special_chars(self):
        valid, _ = validate_name("O'Brien-Smith")
        self.assertTrue(valid)

    def test_name_with_numbers(self):
        valid, _ = validate_name("John123")
        self.assertFalse(valid)


class TestValidateAge(unittest.TestCase):

    def test_valid_age(self):
        valid, _ = validate_age("25")
        self.assertTrue(valid)

    def test_empty_age(self):
        valid, _ = validate_age("")
        self.assertFalse(valid)

    def test_non_numeric_age(self):
        valid, _ = validate_age("abc")
        self.assertFalse(valid)

    def test_negative_age(self):
        valid, _ = validate_age("-5")
        self.assertFalse(valid)


class TestValidateDonorAge(unittest.TestCase):

    def test_valid_donor_age(self):
        valid, _ = validate_donor_age("25")
        self.assertTrue(valid)

    def test_too_young(self):
        valid, msg = validate_donor_age("15")
        self.assertFalse(valid)
        self.assertIn("18", msg)

    def test_too_old(self):
        valid, msg = validate_donor_age("70")
        self.assertFalse(valid)
        self.assertIn("65", msg)

    def test_boundary_18(self):
        valid, _ = validate_donor_age("18")
        self.assertTrue(valid)

    def test_boundary_65(self):
        valid, _ = validate_donor_age("65")
        self.assertTrue(valid)


class TestValidatePhone(unittest.TestCase):

    def test_valid_phone(self):
        valid, _ = validate_phone("9876543210")
        self.assertTrue(valid)

    def test_empty_phone_optional(self):
        valid, _ = validate_phone("")
        self.assertTrue(valid)  # Phone is optional

    def test_phone_with_country_code(self):
        valid, _ = validate_phone("+91 9876543210")
        self.assertTrue(valid)

    def test_short_phone(self):
        valid, _ = validate_phone("12345")
        self.assertFalse(valid)


class TestValidateEmail(unittest.TestCase):

    def test_valid_email(self):
        valid, _ = validate_email("user@example.com")
        self.assertTrue(valid)

    def test_empty_email_optional(self):
        valid, _ = validate_email("")
        self.assertTrue(valid)  # Email is optional

    def test_invalid_email(self):
        valid, _ = validate_email("not-an-email")
        self.assertFalse(valid)


class TestValidateBloodGroup(unittest.TestCase):

    def test_valid_blood_groups(self):
        for bg in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            valid, _ = validate_blood_group(bg)
            self.assertTrue(valid, f"{bg} should be valid")

    def test_invalid_blood_group(self):
        valid, _ = validate_blood_group("X+")
        self.assertFalse(valid)

    def test_empty_blood_group(self):
        valid, _ = validate_blood_group("")
        self.assertFalse(valid)


class TestValidateGender(unittest.TestCase):

    def test_valid_genders(self):
        for g in ["Male", "Female", "Other"]:
            valid, _ = validate_gender(g)
            self.assertTrue(valid)

    def test_invalid_gender(self):
        valid, _ = validate_gender("Unknown")
        self.assertFalse(valid)


class TestValidateOrganType(unittest.TestCase):

    def test_valid_organ(self):
        valid, _ = validate_organ_type("Kidney")
        self.assertTrue(valid)

    def test_invalid_organ(self):
        valid, _ = validate_organ_type("Brain")
        self.assertFalse(valid)


class TestValidateRequired(unittest.TestCase):

    def test_non_empty(self):
        valid, _ = validate_required("hello", "Field")
        self.assertTrue(valid)

    def test_empty(self):
        valid, msg = validate_required("", "Hospital")
        self.assertFalse(valid)
        self.assertIn("Hospital", msg)


class TestValidatePositiveInteger(unittest.TestCase):

    def test_valid(self):
        valid, _ = validate_positive_integer("5", "Units")
        self.assertTrue(valid)

    def test_zero(self):
        valid, _ = validate_positive_integer("0", "Units")
        self.assertFalse(valid)

    def test_negative(self):
        valid, _ = validate_positive_integer("-3", "Units")
        self.assertFalse(valid)

    def test_non_numeric(self):
        valid, _ = validate_positive_integer("abc", "Units")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
