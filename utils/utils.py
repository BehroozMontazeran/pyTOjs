""" Utility class for common functions """

import time
from datetime import datetime

from core.log import Log


class Utils():
    """Utility class for common functions"""
    def __init__(self):
        self.log = Log(self.__class__.__name__)

    def get_timestamp(self):
        """Get the current timestamp"""
        return time.time()

    def get_formatted_time(self, timestamp):
        """Get the formatted time"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

    def timing(self, start_time, end_time, message, msg_type="info"):
        """Print the time taken to run the code with the message and type of message."""

        elapsed_time = end_time - start_time
        elapsed_time_formatted = "{:.4f}".format(elapsed_time)
        if msg_type == "info":
            self.log.info(f"{message}.Time elapsed: {elapsed_time_formatted}")
        elif msg_type == "debug":
            self.log.debug(f"{message}.Time elapsed: {elapsed_time_formatted}")
        elif msg_type == "error":
            self.log.error(f"{message}.Time elapsed: {elapsed_time_formatted}")
        elif msg_type == "warning":
            self.log.warning(f"{message}.Time elapsed: {elapsed_time_formatted}")
