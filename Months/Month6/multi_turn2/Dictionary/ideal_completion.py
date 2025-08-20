guest_directory = {
"Alice": "1111",
"Bob": "2222",
"Charlie": "3333"
}

def process_guest():
    global guest_directory
    # Take user input for name and ID
    name = input("Please enter your name: ")
    id_input = input("Please enter your ID: ")
    # Check if the guest exists and welcome them if they do
    if name in guest_directory:
        if guest_directory[name] == id_input:
            print(f"Welcome {name}!")
        else:
            print("ID does not match our records.")
    else:
        # Validate ID for new guest addition
        if not id_input.isdigit():
            print("Invalid ID. Please enter numeric values only.")
        elif id_input in guest_directory.values():
        # If ID already exists for another guest
            print("This ID is already taken by another guest.")
        else:
        # Add the new guest
            guest_directory[name] = id_input
            print(f"Added {name} with ID {id_input} to the directory.")