
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