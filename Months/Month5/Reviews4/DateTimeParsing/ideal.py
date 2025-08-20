# ideal_completion.py

from datetime import datetime, timezone

def calculate_days_difference(eta):
    # Try to parse the datetime string
    try:
        eta_datetime = datetime.fromisoformat(eta['destinationEta'].replace("Z", "+00:00"))
    except ValueError:
        # Handle case where the datetime might not have timezone information
        eta_datetime = datetime.strptime(eta['destinationEta'], "%Y-%m-%dT%H:%M:%S")
        eta_datetime = eta_datetime.replace(tzinfo=timezone.utc)
    
    # Ensure current datetime is timezone-aware (in UTC)
    current_datetime = datetime.now(timezone.utc)
    
    # If the ETA has a timezone, convert current_datetime to that timezone for accurate comparison
    if eta_datetime.tzinfo is not None:
        current_datetime = current_datetime.astimezone(eta_datetime.tzinfo)
        
    # Calculate the difference in days
    return (current_datetime - eta_datetime.replace(tzinfo=current_datetime.tzinfo)).days