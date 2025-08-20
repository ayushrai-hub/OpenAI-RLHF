guest_directory = {
    "John Doe": "ID001",
    "Jane Smith": "ID002",
    "Alice": "ID003"
}

def process_guest():
    name = input("Please enter your name: ").strip()
    guest_id = input("Please enter your ID: ").strip()

    if not name or not guest_id:
        print("Name and ID must be provided.")
        return

    # Try to convert guest_id to int if possible
    id_to_check = guest_id
    id_value = None
    try:
        id_value = int(guest_id)
    except ValueError:
        id_value = guest_id

    if name in guest_directory:
        stored_id = guest_directory[name]
        # Convert stored id to int if numeric string
        try:
            stored_num = int(stored_id)
        except Exception:
            stored_num = stored_id
        # Determine equality
        if stored_num == id_value:
            print(f"Your invitation code is {guest_id}, Welcome {name} to the event!!")
        else:
            print("The name already included in guests list. Please provide correct ID with the name.")
    else:
        # Validate the ID format.
        if not guest_id.isdigit() or len(guest_id) < 3:
            print("Invalid ID format. ID should be alphanumeric and at least 3 characters long.")
        else:
            # Check for ID uniqueness
            # Check all values in dictionary:
            id_conflict = False
            for val in guest_directory.values():
                # convert val to int if possible
                try:
                    if int(val) == id_value:
                        id_conflict = True
                        break
                except Exception:
                    if val == guest_id:  # fallback
                        id_conflict = True
                        break
            if id_conflict:
                print("This ID is being used already. Please try another one.")
            else:
                # Add the new guest to the directory
                # Add id_value as int if conversion succeeded; else use string
                # We purposely convert to int for numeric
                try:
                    guest_directory[name] = int(guest_id)
                except ValueError:
                    guest_directory[name] = guest_id
                print(f"The new guest {name} has been added with ID {guest_id}.")