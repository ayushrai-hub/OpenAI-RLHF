import re
from datetime import datetime

class Client:
    def __init__(self, first_name, middle_name, last_name, address, city, state, postal_code, contact_number, emergency_contact_name, emergency_contact_number):
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

    def get_first_name(self):
        return self.first_name

    def set_first_name(self, value):
        self.first_name = value

    def get_middle_name(self):
        return self.middle_name

    def set_middle_name(self, value):
        if not any(char.isdigit() for char in value):
            self.middle_name = value
        else:
            raise ValueError("Middle initial can't have numbers.")

    def get_last_name(self):
        return self.last_name

    def set_last_name(self, value):
        self.last_name = value

    def get_address(self):
        return self.address

    def set_address(self, value):
        self.address = value

    def get_city(self):
        return self.city

    def set_city(self, value):
        self.city = value

    def get_state(self):
        return self.state

    def set_state(self, value):
        self.state = value

    def get_postal_code(self):
        return self.postal_code

    def set_postal_code(self, value):
        if re.match(r'^\d{5}$', value):
            self.postal_code = value
        else:
            raise ValueError("Zip code needs to be a 5-digit number.")

    def get_contact_number(self):
        return self.contact_number

    def set_contact_number(self, value):
        if re.match(r'^\d{10}$', value):
            self.contact_number = value
        else:
            raise ValueError("Phone number needs to be a 10-digit number.")

    def get_emergency_contact_name(self):
        return self.emergency_contact_name

    def set_emergency_contact_name(self, value):
        self.emergency_contact_name = value

    def get_emergency_contact_number(self):
        return self.emergency_contact_number

    def set_emergency_contact_number(self, value):
        if re.match(r'^\d{10}$', value):
            self.emergency_contact_number = value
        else:
            raise ValueError("Urgent contact number needs to be a 10-digit number.")
        
    def to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(f"{self.first_name}\n{self.middle_name}\n{self.last_name}\n{self.address}\n{self.city}\n{self.state}\n{self.postal_code}\n{self.contact_number}\n{self.emergency_contact_name}\n{self.emergency_contact_number}\n")

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            return Client(*[line.strip() for line in lines])

class Treatment:
    def __init__(self, name, date, practitioner, charges):
        self.name = name
        self.date = self.validate_date(date)
        self.practitioner = practitioner
        self.charges = self.validate_charges(charges)

    def validate_date(self, date):
        try:
            return datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    def validate_charges(self, charges):
        try:
            charges = float(charges)
            if charges < 0:
                raise ValueError
            return charges
        except ValueError:
            raise ValueError("Charges must be a non-negative number.")

    # Getter and setter methods for all attributes
    # Each setter includes appropriate validation

    def to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(f"{self.name}\n{self.date}\n{self.practitioner}\n{self.charges}\n")

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            return Treatment(lines[0].strip(), lines[1].strip(), lines[2].strip(), float(lines[3].strip()))

def get_validated_input(prompt, validation_func):
    while True:
        try:
            user_input = input(prompt)
            return validation_func(user_input)
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

def validate_non_empty(value):
    if not value.strip():
        raise ValueError("This field cannot be empty")
    return value.strip()

def validate_zip_code(value):
    if not re.match(r'^\d{5}$', value):
        raise ValueError("Zip code must be a 5-digit number")
    return value

def validate_phone_number(value):
    if not re.match(r'^\d{10}$', value):
        raise ValueError("Phone number must be a 10-digit number")
    return value

def main():
    # Get client information
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

    client.to_file("client.txt")

    # Get treatment information
    treatments = []
    while True:
        try:
            num_treatments = int(get_validated_input("Enter number of treatments: ", lambda x: int(x) if int(x) > 0 else ValueError("Number of treatments must be positive")))
            break
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

    for i in range(num_treatments):
        treatment = Treatment(
            get_validated_input(f"Enter title of treatment {i+1}: ", validate_non_empty),
            get_validated_input(f"Enter date of treatment {i+1} (YYYY-MM-DD): ", lambda x: x),
            get_validated_input(f"Enter practitioner's name for treatment {i+1}: ", validate_non_empty),
            get_validated_input(f"Enter cost for treatment {i+1}: ", lambda x: float(x) if float(x) >= 0 else ValueError("Cost must be non-negative"))
        )
        treatment.to_file(f"treatment_{i+1}.txt")
        treatments.append(treatment)

    # Display client information
    client = Client.from_file("client.txt")
    print("\nClient Information:")
    print(f"Name: {client.first_name} {client.middle_name} {client.last_name}")
    print(f"Address: {client.address}, {client.city}, {client.state} {client.postal_code}")
    print(f"Phone: {client.contact_number}")
    print(f"Emergency Contact: {client.emergency_contact_name} ({client.emergency_contact_number})")

    # Display treatment information and calculate total cost
    total_cost = 0
    print("\nTreatment Information:")
    for i, treatment in enumerate(treatments, 1):
        treatment = Treatment.from_file(f"treatment_{i}.txt")
        print(f"\nTreatment {i}:")
        print(f"Title: {treatment.name}")
        print(f"Date: {treatment.date}")
        print(f"Practitioner: {treatment.practitioner}")
        print(f"Cost: ${treatment.charges:.2f}")
        total_cost += treatment.charges

    print(f"\nTotal Cost of Treatments: ${total_cost:.2f}")

if __name__ == "__main__":
    main()