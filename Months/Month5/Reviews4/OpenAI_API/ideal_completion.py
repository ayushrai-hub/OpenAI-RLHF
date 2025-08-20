# ideal_completion.py

import os
from openai import OpenAI

# Function to get a response from the OpenAI API
def get_chatgpt_response(prompt):

    client = OpenAI()

    return client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    ).choices[0].message.content