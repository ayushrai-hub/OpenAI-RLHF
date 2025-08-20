
import re
from typing import Callable

class Client:
    def __init__(self, first_name: str, middle_name: str, last_name: str, address: str, city: str, state: str, postal_code: str, contact_number: str, emergency_contact_name: str, emergency_contact_number: str) -> None:
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.contact_number = contact_number
        self.emergency_contact_name = emergency_contact_name
        self.emergency_contact_number = emergency_contact_number

    def to_file(self, filename: str) -> None:
        with open(filename, 'w') as file:
            file.write(f"{self.first_name}\n{self.middle_name}\n{self.last_name}\n{self.address}\n{self.city}\n{self.state}\n{self.postal_code}\n{self.contact_number}\n{self.emergency_contact_name}\n{self.emergency_contact_number}\n")

    @staticmethod
    def from_file(filename: str) -> "Client":
        with open(filename, 'r') as file:
            lines = file.readlines()
            return Client(
                first_name=lines[0].strip(),
                middle_name=lines[1].strip(),
                last_name=lines[2].strip(),
                address=lines[3].strip(),
                city=lines[4].strip(),
                state=lines[5].strip(),
                postal_code=lines[6].strip(),
                contact_number=lines[7].strip(),
                emergency_contact_name=lines[8].strip(),
                emergency_contact_number=lines[9].strip()
            )

class Treatment:
    def __init__(self, name: str, date: str, practitioner: str, charges: str) -> None:
        self.name = name
        self.date = date
        self.practitioner = practitioner
        self.charges = charges

    def to_file(self, filename: str) -> None:
        with open(filename, 'w') as file:
            file.write(f"{self.name}\n{self.date}\n{self.practitioner}\n{self.charges}\n")

    @staticmethod
    def from_file(filename: str) -> "Treatment":
        with open(filename, 'r') as file:
            lines = file.readlines()
            return Treatment(
                name=lines[0].strip(),
                date=lines[1].strip(),
                practitioner=lines[2].strip(),
                charges=lines[3].strip()
            )

# Input validation functions
def validate_non_empty(value: str) -> str:
    if not value.strip():
        raise ValueError("This field cannot be empty.")
    return value

def validate_zip_code(value: str) -> str:
    if not re.match(r'^\d{5}$', value):
        raise ValueError("Zip code needs to be a 5-digit number.")
    return value

def validate_phone_number(value: str) -> str:
    if not re.match(r'^\d{10}$', value):
        raise ValueError("Phone number needs to be a 10-digit number.")
    return value

def get_validated_input(prompt: str, validation_func: Callable[[str], any]) -> any:
    while True:
        try:
            value = input(prompt)
            return validation_func(value)
        except ValueError as e:
            print(f"Error: {e}")
