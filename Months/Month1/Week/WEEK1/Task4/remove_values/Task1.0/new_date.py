import dateparser
from dateutil.parser import parse
from datetime import datetime, timedelta

def parse_reminder(input_text):
    now = datetime.now()
    
    # Replace 'tomorrow' with actual date
    if 'tomorrow' in input_text.lower():
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        input_text = input_text.lower().replace('tomorrow', tomorrow)

    # Try to parse the entire input as a date/time
    try:
        reminder_time = parse(input_text, fuzzy=True, default=now)
        return input_text, reminder_time
    except ValueError:
        pass

    # Search for date/time expressions in the input text
    reminder_time = dateparser.parse(input_text, settings={'PREFER_DATES_FROM': 'future'})
    if reminder_time:
        # Find the date/time string in the original input
        date_str = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
        parts = input_text.lower().split()
        for i, word in enumerate(parts):
            if any(time_word in word for time_word in ['am', 'pm', 'today', 'next', 'in']):
                date_str = ' '.join(parts[i:])
                break

        # Remove the date/time part from the input text to get the reminder message
        reminder_message = input_text.replace(date_str, '').strip()
        reminder_message = reminder_message.rstrip('at').strip()
    else:
        # If no date/time is found, return the original message and None
        reminder_message = input_text
        reminder_time = None

    return reminder_message, reminder_time

def format_reminder(input_text):
    reminder_message, reminder_time = parse_reminder(input_text)
    if reminder_time:
        if reminder_time.time() == datetime.min.time():
            formatted_time = reminder_time.strftime("%Y-%m-%d 00:00:00")
        else:
            formatted_time = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"Reminder: {reminder_message} at {formatted_time}"
    else:
        return f"Reminder: {reminder_message}"

# Example usage
input_texts = [
    "Remind me to call John at 3 PM",
    "I have a meeting tomorrow",
    "My doctor's appointment is next Monday",
    "Remind me to check the oven in 10 minutes"
]

for input_text in input_texts:
    print(format_reminder(input_text))