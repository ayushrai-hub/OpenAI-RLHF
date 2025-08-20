# ideal_completion.py

class Storage:
    """Class to represent a backup task."""

    def __init__(self, info_size, storage_speed):
        """
        Initialize the Storage object with info size and storage speed.

        :param info_size: Data volume to be stored in gigabytes.
        :param storage_speed: Storage speed in gigabytes per second.
        """
        self.info_size = info_size
        self.storage_speed = storage_speed

    def start_backup(self):
        """
        Simulate the backup process by calculating the duration.

        :return: A tuple (duration, success_status)
                 - duration: Time required to complete the backup in seconds.
                 - success_status: True if backup is successful, False otherwise.
        """
        # Check for division by zero and raise an error if storage speed is zero
        if self.storage_speed == 0:
            raise ZeroDivisionError("Storage speed cannot be zero.")

        # Calculate the duration of the backup
        duration = self.info_size / self.storage_speed

        # Determine if the backup is successful (duration <= 60 seconds)
        success = duration <= 60

        # Return the duration and success status
        return duration, success