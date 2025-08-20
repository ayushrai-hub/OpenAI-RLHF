import unittest
from unittest.mock import patch
import io
import sys
from datetime import datetime
import os

from ideal_completion import Client, Treatment,  validate_non_empty, validate_zip_code, validate_phone_number, get_validated_input

class TestClientManagement(unittest.TestCase):

    def setUp(self):
        # It initializes a client and treatment object for use in tests
        self.client = Client("John", "M", "Doe", "123 Main St", "Anytown", "CA", "12345", "1234567890", "Jane Doe", "9876543210")
        self.treatment = Treatment("Checkup", "2023-05-01", "Dr. Smith", 100.00)
    # This tests if the client object is correctly initialized with the given attributes.
    def test_client_initialization(self):
        self.assertEqual(self.client.first_name, "John")
        self.assertEqual(self.client.middle_name, "M")
        self.assertEqual(self.client.last_name, "Doe")
        self.assertEqual(self.client.address, "123 Main St")
        self.assertEqual(self.client.city, "Anytown")
        self.assertEqual(self.client.state, "CA")
        self.assertEqual(self.client.postal_code, "12345")
        self.assertEqual(self.client.contact_number, "1234567890")
        self.assertEqual(self.client.emergency_contact_name, "Jane Doe")
        self.assertEqual(self.client.emergency_contact_number, "9876543210")
    
    def test_client_setters(self):
        # This test the setter methods of the client class
        self.client.set_first_name("Jane")
        self.assertEqual(self.client.get_first_name(), "Jane")
        # This tests that invalid middle name(non-single character) raises ValueError
        with self.assertRaises(ValueError):
            self.client.set_middle_name("M1")
        # This tests that invalid postal code (not 5 digits) raises ValueError
        with self.assertRaises(ValueError):
            self.client.set_postal_code("1234")
        # This test that invalid phone number (not 10 digits) raises ValueError
        with self.assertRaises(ValueError):
            self.client.set_contact_number("123456789")

    def test_client_file_io(self):
        # This test ensures that that client data can be persistently stored and retrived correctly
        self.client.to_file("test_client.txt")
        loaded_client = Client.from_file("test_client.txt")
        self.assertEqual(self.client.first_name, loaded_client.first_name)
        self.assertEqual(self.client.last_name, loaded_client.last_name)
        os.remove("test_client.txt")
        
    def test_treatment_initialization(self):
        # This test ensure that the constructor properly sets all the treatment information
        self.assertEqual(self.treatment.name, "Checkup")
        self.assertEqual(self.treatment.date, datetime(2023, 5, 1).date())
        self.assertEqual(self.treatment.practitioner, "Dr. Smith")
        self.assertEqual(self.treatment.charges, 100.00)

    def test_treatment_validation(self):
        # This test ensure tha that the treatment class properly validates its inputs
        with self.assertRaises(ValueError):
            Treatment("Invalid", "2023-13-01", "Dr. Who", 100.00)  # Invalid date

        with self.assertRaises(ValueError):
            Treatment("Invalid", "2023-05-01", "Dr. Who", -100.00)  # Negative charges

    def test_treatment_file_io(self):
        # This test ensures that treatment data can be persistently stored and retrieved correctly
        self.treatment.to_file("test_treatment.txt")
        loaded_treatment = Treatment.from_file("test_treatment.txt")
        self.assertEqual(self.treatment.name, loaded_treatment.name)
        self.assertEqual(self.treatment.date, loaded_treatment.date)
        self.assertEqual(self.treatment.practitioner, loaded_treatment.practitioner)
        self.assertEqual(self.treatment.charges, loaded_treatment.charges)
        os.remove("test_treatment.txt")

    def test_validate_non_empty(self):
        # This test ensures that empty strings are rejected and non-empty strings are accepted
        self.assertEqual(validate_non_empty("Test"), "Test")
        with self.assertRaises(ValueError):
            validate_non_empty("")

    def test_validate_zip_code(self):
        # This test ensures that only valid 5-digit zip codes are accepted
        self.assertEqual(validate_zip_code("12345"), "12345")
        with self.assertRaises(ValueError):
            validate_zip_code("1234")
        with self.assertRaises(ValueError):
            validate_zip_code("123456")

    def test_validate_phone_number(self):
        # This test ensures that only valid 10-digit phone numbers are accepted
        self.assertEqual(validate_phone_number("1234567890"), "1234567890")
        with self.assertRaises(ValueError):
            validate_phone_number("123456789")
        with self.assertRaises(ValueError):
            validate_phone_number("12345678901")

    @patch('builtins.input', side_effect=['John', 'M', 'Doe', '123 Main St', 'Anytown', 'CA', '12345', '1234567890', 'Jane Doe', '9876543210'])
    def test_get_validated_input(self, mock_input):
        # This test ensures that the function correctly prompts for and validates user input
        client = Client(
            get_validated_input("Enter first name: ", validate_non_empty),
            get_validated_input("Enter middle initial: ", lambda x: x if x else " "),
            get_validated_input("Enter last name: ", validate_non_empty),
            get_validated_input("Enter address: ", validate_non_empty),
            get_validated_input("Enter city: ", validate_non_empty),
            get_validated_input("Enter state: ", validate_non_empty),
            get_validated_input("Enter zip code: ", validate_zip_code),
            get_validated_input("Enter phone number: ", validate_phone_number),
            get_validated_input("Enter emergency contact name: ", validate_non_empty),
            get_validated_input("Enter emergency contact number: ", validate_phone_number)
        )
        self.assertEqual(client.first_name, "John")
        self.assertEqual(client.middle_name, "M")
        self.assertEqual(client.last_name, "Doe")
        self.assertEqual(client.address, "123 Main St")
        self.assertEqual(client.city, "Anytown")
        self.assertEqual(client.state, "CA")
        self.assertEqual(client.postal_code, "12345")
        self.assertEqual(client.contact_number, "1234567890")
        self.assertEqual(client.emergency_contact_name, "Jane Doe")
        self.assertEqual(client.emergency_contact_number, "9876543210")

if __name__ == '__main__':
    unittest.main(verbosity=2)