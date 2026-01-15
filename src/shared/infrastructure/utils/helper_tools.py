"""Helper utilities - timing decorator and other tools."""
import time
import functools


def timer(func):
    """Decorator that prints function runtime."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(" ====> Duration {:.2f} secs: {}".format(run_time, func.__doc__))
        return value
    return wrapper_timer
