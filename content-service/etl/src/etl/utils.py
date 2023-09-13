import time
from functools import wraps
from typing import Generator


def backoff(logging, start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10):
    """
    Function to call decorated function after some time interval in case
    of an exception. Uses an exponential time interval growth until it
    reaches given upper waiting interval.

    Args:
        logging: logging module
        start_sleep_time: initial waiting time interval.
        factor: factor for exponential growth.
        border_sleep_time: upper boundary of waiting time inverval.

    Returns: decorated function returned object.
    """

    def exponential_backoff() -> Generator[float, None, None]:
        time_wait = start_sleep_time
        while True:
            time_wait *= factor
            time_wait = min(time_wait, border_sleep_time)
            yield time_wait

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                wait_sec = next(exponential_backoff())
                logging.exception(f"Error from {func.__name__}: {err}. Waiting {wait_sec}...")
                time.sleep(wait_sec)

        return inner

    return func_wrapper
