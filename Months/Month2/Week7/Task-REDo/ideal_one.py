from datetime import datetime
import pytz

def convert_utc_to_est():
    # Define the timezone you want to convert to
    utc = pytz.UTC
    est = pytz.timezone('US/Eastern')
    
    # Current UTC time
    utc_time = datetime.now(pytz.utc)
    
    # Convert UTC time to EST
    est_time = utc_time.astimezone(est)
    
    return utc_time, est_time

if __name__ == '__main__':
    utc_time, est_time = convert_utc_to_est()
    
    print("UTC time:", utc_time)
    print("EST time:", est_time)