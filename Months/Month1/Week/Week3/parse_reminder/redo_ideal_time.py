import dateparser
from dateparser import search

def parse_reminder(input_text):
    # Define the settings for dateparser
    settings = {
        'PREFER_DATES_FROM': 'future' if 'next' in input_text.lower() else 'current_period',
    }
    
    # Search for date and time expressions in the input text
    search_results = dateparser.search.search_dates(
        input_text,
        languages=['en'],
        settings=settings
    )
    
    if search_results:
        # Extract the first found date/time and its corresponding string
        datetime_str, reminder_time = search_results[0]
        
        # Check if the identified date phrase indicates a full day without time
        reminder_time = reminder_time.replace(microsecond=0)
        
        # Handle specific date phrases
        if datetime_str.lower() in ["tomorrow"]:  # Add more terms as needed
            reminder_time = reminder_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Remove the datetime part from the input text to get the reminder message
        reminder_message = input_text.replace(datetime_str, "").strip()
        reminder_message = reminder_message.replace("next", "").replace("previous", "").strip()
    else:
        # If no date/time is found, return the original message and None
        reminder_message = input_text
        reminder_time = None
    
    return reminder_message, reminder_time

# Example usage
input_texts = [
    "Remind me to call John at 3 PM",
    "I have a meeting tomorrow",
    "My doctor's appointment is next Monday",
    "Remind me to check the oven in 10 minutes"
]

for input_text in input_texts:
    reminder_message, reminder_time = parse_reminder(input_text)
    print(f"Reminder: {reminder_message} at {reminder_time}")
