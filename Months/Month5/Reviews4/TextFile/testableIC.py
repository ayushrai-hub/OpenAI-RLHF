def extract_numbers_from_string(file_path):
    with open(file_path, 'r') as file:
        data = file.read().strip()  # Read and strip any extra whitespace

    try:
        number = int(data)  # Convert to integer
        return number
    except ValueError:
        return None  # Return None if the file does not contain a valid integer
