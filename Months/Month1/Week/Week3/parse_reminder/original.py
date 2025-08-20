import dateparser
from dateparser import search
from typing import Tuple, Optional
from datetime import datetime

def parse_reminder(input_text: str) -> Tuple[str, Optional[datetime]]:
    # Use search_dates to find dates in the input text
    search_results = search.search_dates(input_text, settings={'PREFER_DATES_FROM': 'future'})

    if search_results:
        # Extract the first found date/time and its corresponding string
        datetime_str, reminder_time = search_results[0]
        # Remove the datetime part from the input text to get the reminder message
        reminder_message = input_text.replace(datetime_str, "").strip()
        # Ensure microseconds are set to 0
        reminder_time = reminder_time.replace(microsecond=0)
    else:
        # If no date/time is found, return the original message and None
        reminder_message = input_text
        reminder_time = None

    return reminder_message, reminder_time
