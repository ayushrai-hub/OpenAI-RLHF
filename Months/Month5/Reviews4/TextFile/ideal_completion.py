import re

def extract_numbers_from_string(data):
    try:
        # Regular expression to find all sequences of digits
        pattern = r'\d+'
        
        # Find all substrings that match the pattern
        matches = re.findall(pattern, data)
        
        # Convert all matched substrings to integers
        numbers = [int(match) for match in matches]
        
        return numbers
    except ValueError:
        print("The file does not contain a valid integer.")
        return []