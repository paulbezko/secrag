from datetime import datetime
import time
import threading

class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit  # Maximum number of calls per second
        self.semaphore = threading.Semaphore(rate_limit)
        self.lock = threading.Lock()
        self.reset_time = time.time() + 1

    def current_time(self):
        """Helper function to get current time in yyyy-mm-dd : hh-mm-ss.ms format."""
        return datetime.now().strftime('%Y-%m-%d : %H-%M-%S.%f')[:-3]

    def acquire(self):
        with self.lock:
            current_time = time.time()
            if current_time >= self.reset_time:
                # Reset the semaphore and reset_time every second
                self.semaphore = threading.Semaphore(self.rate_limit)
                self.reset_time = current_time + 1

        # Check if semaphore is already exhausted
        if self.semaphore._value == 0:
            print(f"Rate limit exceeded at {self.current_time()} - waiting for capacity")

        # Block until semaphore is acquired (no timeout, it will wait)
        self.semaphore.acquire()
        # print(f"Semaphore acquired at {self.current_time()}")

    def release(self):
        self.semaphore.release()


def try_or(func, default=None, expected_exc=(Exception,)):
    """
    Tries to execute a given function, and if it fails with one of the specified
    exceptions, returns a default value instead.

    :param func: The function to try to execute
    :param default: The value to return if an exception is raised
    :param expected_exc: A tuple of exception types that are expected to be raised
    :return: The result of the function, or the default value if an exception was
             raised
    """
    try:
        return func()
    except expected_exc:
        return default


def compare_year(date, input_year_str):
    """
    Compare the year extracted from a datetime object with a given input year string.

    Args:
        date (datetime): A datetime object.
        input_year_str (str): The year to compare with, as a string.

    Returns:
        bool: True if the extracted year matches the input year string, False otherwise.
    """    
    # Parse the date string into a datetime object
    date_obj = date
    
    # Extract the year from the datetime object
    year = date_obj.year
    
    # Convert the year to string
    year_str = str(year)
    
    # Compare the extracted year with the input year string
    if year_str == input_year_str:
        return True
    else:
        return False