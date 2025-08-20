from datetime import datetime
import pytz

def convert_utc_to_est(utc_time):
    # Define the timezone you want to convert to
    est = pytz.timezone('US/Eastern')
    
    # Ensure the input time is UTC
    if utc_time.tzinfo != pytz.utc:
        utc_time = utc_time.replace(tzinfo=pytz.utc)
    
    # Convert UTC time to EST
    est_time = utc_time.astimezone(est)
    return est_time

def main():
    # Current UTC time
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    
    # Convert UTC time to EST
    est_time = convert_utc_to_est(utc_time)
    
    print("UTC time:", utc_time)
    print("EST time:", est_time)

if __name__ == "__main__":
    main()