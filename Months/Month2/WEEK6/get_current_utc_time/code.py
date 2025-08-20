from datetime import datetime, timezone
import pytz

def get_current_utc_time():
    return datetime.now(timezone.utc)

def convert_utc_to_est(utc_time):
    est = pytz.timezone('US/Eastern')
    return utc_time.astimezone(est)

if __name__ == '__main__':
    utc_time = get_current_utc_time()
    est_time = convert_utc_to_est(utc_time)
    
    print("UTC time:", utc_time)
    print("EST time:", est_time)