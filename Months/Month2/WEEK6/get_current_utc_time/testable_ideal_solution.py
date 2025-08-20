
from datetime import datetime
import pytz

def convert_utc_to_est():
    est = pytz.timezone('US/Eastern')
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    est_time = utc_time.astimezone(est)
    return utc_time, est_time
