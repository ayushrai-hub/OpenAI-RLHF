import dateparser
from dateparser import search
from datetime import datetime, timedelta

def parse_reminder(input_text):
    # Define the settings for dateparser
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now(),
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
        
        # Remove the datetime part from the input text to get the reminder message
        reminder_message = input_text.replace(datetime_str, "").strip()
        reminder_message = reminder_message.replace("next", "").strip()

        # Handle full day events (no specific time mentioned)
        
        # Handle "next" day cases
        if "next" in input_text.lower():
            current_date = datetime.now().date()
            if reminder_time.date() <= current_date:
                # If the parsed date is not in the future, add 7 days
                reminder_time += timedelta(days=7)
        
        # Remove microseconds for consistency
        reminder_time = reminder_time.replace(microsecond=0)
    else:
        # If no date/time is found, return the original message and None
        reminder_message = input_text
        reminder_time = None
    
    return reminder_message, reminder_time