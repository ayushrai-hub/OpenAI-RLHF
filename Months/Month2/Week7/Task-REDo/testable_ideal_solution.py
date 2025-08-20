from datetime import datetime
import pytz

def convert_utc_to_est():
    # Define the timezone you want to convert to
    est = pytz.timezone('US/Eastern')

    # Current UTC time
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)

    # Convert UTC time to EST
    est_time = utc_time.astimezone(est)

    return utc_time, est_time
