# ideal_completion.py

import subprocess

def execute_python_code(code, output_file=None):
    subprocess.run(
        ['python', '-c', code],
        text=True
    )