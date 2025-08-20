# ideal_completion.py

import os
import re
import shutil

# Function to extract the value within square brackets
def extract_value(filename):
    match = re.search(r'\[(\w+)\]', filename)  # Match both alphabetic and numeric inside square brackets
    if match:
        value = match.group(1)
        if value.isdigit():
            return value, 'digit'
        else:
            return value, 'alpha'
    return None, None

# Function to get the base name without the value in square brackets
def get_base_name(filename):
    return re.sub(r'\[\w+\]', '', filename)  # Correct regex to remove [<value>] from filename

def processing(directory):
    # Ensure the _SS directory exists
    ss_directory = os.path.join(directory, "_SS")
    os.makedirs(ss_directory, exist_ok=True)

    # Dictionary to store files by their base name
    files_dict = {}

    # Iterate over files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            value, value_type = extract_value(filename)
            if value is not None:
                base_name = get_base_name(filename)
                if base_name not in files_dict:
                    files_dict[base_name] = []
                files_dict[base_name].append((filename, value, value_type))

    # Compare pairs of files and move according to the conditions
    for base_name, files in files_dict.items():
        if len(files) == 2:
            file1, value1, type1 = files[0]
            file2, value2, type2 = files[1]

            if (type1 == 'alpha' and type2 == 'digit'):
                shutil.move(os.path.join(directory, file1), ss_directory)
                print(f"Moved {file1} to {ss_directory}")
            elif (type1 == 'digit' and type2 == 'alpha'):
                shutil.move(os.path.join(directory, file2), ss_directory)
                print(f"Moved {file2} to {ss_directory}")


if __name__ == "__main__":
    processing("./")