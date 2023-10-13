import logging
import time


class Sleeper:
    """Pauses the process with linearly increasing pause interval."""

    def __init__(self, sleep_init: int = 5, sleep_increase: int | None = 5):
        self.sleep_init = sleep_init
        self.sleep_increase = sleep_increase

        self.sleep_val = sleep_init

    def sleep(self, msg: str = "", sleep_secs: float | None = None):
        logging.info(f"{msg}: Pausing for {self.sleep_val} secs...")

        if sleep_secs is None:
            time.sleep(self.sleep_val)
        else:
            time.sleep(sleep_secs)

        if self.sleep_increase is not None:
            self.sleep_val += self.sleep_increase

    def reset(self):
        self.sleep_val = self.sleep_init
