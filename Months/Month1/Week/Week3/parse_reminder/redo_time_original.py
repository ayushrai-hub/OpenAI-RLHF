import dateparser.search

def parse_reminder(input_text):
    # Use SearchWithDetection to find dates in the input text
    search = dateparser.search.SearchWithDetection()
    search_results = search.search_dates(input_text)

    if search_results:
        # Extract the first found date/time and its corresponding string
        datetime_str, reminder_time = search_results[0]
        # Remove the datetime part from the input text to get the reminder message
        reminder_message = input_text.replace(datetime_str, "").strip()
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
