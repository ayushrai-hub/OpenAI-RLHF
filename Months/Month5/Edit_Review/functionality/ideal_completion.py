# ideal_completion.py
import requests
import subprocess
import json

def fetch_codegen_output(prompt_input):
    service_url = "https://api.codegenapi.net/chat/responses"
    header_info = {
        "Authorization": "Bearer <REPLACE_WITH_YOUR_KEY>",  # Insert your API key
        "Content-Type": "application/json"
    }
    request_payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": prompt_input
            }
        ],
        "max_tokens": 512,
        "stream": False
    }

    try:
        api_response = requests.post(service_url, headers=header_info, data=json.dumps(request_payload))
        api_response.raise_for_status()
        api_output = api_response.json()
        # Extract the content from the response
        python_code = api_output['choices'][0]['message']['content'].strip()
        return python_code
    except Exception as err:
        print(f"Error making request to API: {err}")
        return None

def write_code_to_file(python_filename, python_code):
    try:
        with open(python_filename, 'w', encoding='utf-8') as f:
            f.write(python_code)
        print(f"File successfully saved: {python_filename}")
    except UnicodeEncodeError as err:
        print(f"Unicode encoding error: {err}")
    except Exception as err:
        print(f"An error occurred while saving the file: {err}")

def run_code_from_file(python_filename):
    try:
        if python_filename.endswith(".py"):
            subprocess.run(['python', python_filename], check=True)
        else:
            print(f"Execution not supported for this file type: {python_filename}")
    except Exception as err:
        print(f"Problem executing the code: {err}")

def main_routine():
    template_prompt = """You are an AI Programmer capable of crafting coding projects. You output only code, no additional text, purely Python. In an example where a user requests an HTML document, JavaScript, and CSS, you'll provide these files exclusively. But first, how to create them? You execute a Python script to generate these 3 files.

User requested :"""

    # Sample user input
    user_input = "Construct a straightforward webpage featuring HTML, CSS, and JavaScript"

    combined_prompt = template_prompt + user_input

    # Fetch generated code from API
    code_generated = fetch_codegen_output(combined_prompt)
    if code_generated:
        code_generated = code_generated.replace("```python", "").replace("```", "").strip()

        # Save the Python code to a file
        script_file = "file_creator.py"
        write_code_to_file(script_file, code_generated)

        # Run the saved Python script
        run_code_from_file(script_file)

if __name__ == "__main__":
    main_routine()