import logging
from time import sleep
from functools import wraps
import requests


def backoff(max_retries):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for n in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException:
                    sleep((2**n) + 0.2)  # exponential back-off
            logging.warning(f"Failed to execute {func.__name__} after {max_retries} attempts.")

        return wrapper

    return decorator
