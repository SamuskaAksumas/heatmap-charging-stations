"""
Helper utilities for the application.

Contains timing decorators and other utility functions.
"""
import time
import functools


def timer(func):
    """
    Decorator that prints the runtime of the decorated function.

    Args:
        func: The function to be timed.

    Returns:
        Wrapper function that times execution and prints duration.
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(" ====> Duration {:.2f} secs: {}".format(run_time, func.__doc__))
        return value
    return wrapper_timer
