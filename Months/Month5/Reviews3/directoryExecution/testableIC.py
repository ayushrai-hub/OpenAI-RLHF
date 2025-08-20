import os
import subprocess

# Writes the code to a file
def write_code_to_file(python_filename, python_code):
    try:
        with open(python_filename, 'w', encoding='utf-8') as f:
            f.write(python_code)
        print(f"File successfully saved: {python_filename}")
    except UnicodeEncodeError as err:
        print(f"Unicode encoding error: {err}")
    except Exception as err:
        print(f"An error occurred while saving the file: {err}")

# Runs the code from the specified file
def run_code_from_file(python_filename):
    try:
        # Determines the file type and executes accordingly
        if python_filename.endswith(".py"):
            subprocess.run(['python', python_filename], check=True)
        else:
            print(f"Execution not supported for this file type: {python_filename}")
    except Exception as err:
        print(f"Problem executing the code: {err}")

# Function to execute python code provided as a string
def execute_python_code(code: str, output_file: str = None):
    script_file = output_file if output_file else "temp_code.py"
    write_code_to_file(script_file, code)
    run_code_from_file(script_file)
