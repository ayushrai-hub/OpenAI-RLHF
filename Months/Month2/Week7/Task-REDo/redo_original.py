from datetime import datetime
import pytz
def main():

    # Define the timezone you want to convert to
    est = pytz.timezone('US/Eastern')

    # Current UTC time
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)

    # Convert UTC time to EST
    est_time = utc_time.astimezone(est)

    print("UTC time:", utc_time)
    print("EST time:", est_time)

if __name__ == "__main__":
    main()