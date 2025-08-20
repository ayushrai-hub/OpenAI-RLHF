from datetime import datetime, timedelta
import re

def parse_reminder(input_text, base_date):
    # Regular expressions for common time formats
    time_patterns = [
        r'(\d{1,2})\s*(am|pm)', # 3 PM
        r'(\d{1,2}):(\d{2})', # 15:00
        r'in\s+(\d+)\s+(minute|hour|day)s?' # in 10 minutes
    ]
    # Check for time patterns
    for pattern in time_patterns:
        match = re.search(pattern, input_text, re.IGNORECASE)
        if match:
            if 'am' in match.group().lower() or 'pm' in match.group().lower():
                time = datetime.strptime(match.group(), "%I %p").time()
                reminder_message = re.sub(r'\s*at\s*' + re.escape(match.group()), '', input_text).strip()
            elif ':' in match.group():
                time = datetime.strptime(match.group(), "%H:%M").time()
                reminder_message = re.sub(r'\s*at\s*' + re.escape(match.group()), '', input_text).strip()
            else:
                # Handle "in X minutes/hours/days"
                value = int(match.group(1))
                unit = match.group(2).lower()
                if unit.startswith('minute'):
                    delta = timedelta(minutes=value)
                elif unit.startswith('hour'):
                    delta = timedelta(hours=value)
                else:
                    delta = timedelta(days=value)
                time = (base_date + delta).time()
                reminder_message = re.sub(r'\s*' + re.escape(match.group()), '', input_text).strip()
            
            reminder_time = datetime.combine(base_date.date(), time)
            return reminder_message, reminder_time.strftime('%H:%M:%S')

    # Check for relative days
    if 'tomorrow' in input_text.lower():
        reminder_time = base_date + timedelta(days=1)
        reminder_message = input_text.replace('tomorrow', '').strip()
        return reminder_message, reminder_time.strftime('%Y-%m-%d 00:00:00')
    elif 'next monday' in input_text.lower():
        days_ahead = 7 - base_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        reminder_time = base_date + timedelta(days=days_ahead)
        reminder_message = input_text.replace('next Monday', '').strip()
        return reminder_message, reminder_time.strftime('%Y-%m-%d 00:00:00')

    # If no time information found
    return input_text, None

# Set the base date for relative date parsings
base_date = datetime.now()  # Assuming current time is 14:25

# Example usage
input_texts = [
    "Remind me to call John at 3 PM",
    "I have a meeting tomorrow",
    "My doctor's appointment is next Monday",
    "Remind me to check the oven in 10 minutes"
]

for input_text in input_texts:
    reminder_message, reminder_time = parse_reminder(input_text, base_date)
    print(f"Reminder: {reminder_message} at {reminder_time}")