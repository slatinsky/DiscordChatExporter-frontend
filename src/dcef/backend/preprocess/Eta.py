import time

from Formatters import Formatters


class Eta:
    def __init__(self, max_value, count):
        self.bulgarian_constant = 50000
        self.max_value = max_value + count * self.bulgarian_constant
        self.current_value = 0
        self.time_started = time.time()
        self.last_increment_time = self.time_started

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            raise exc_type(exc_value).with_traceback(exc_traceback)
        return True

    def calculate_eta(self):
        if self.current_value == 0:
            return "N/A"
        else:
            eta = (time.time() - self.time_started) / self.current_value * (self.max_value - self.current_value) - (time.time() - self.last_increment_time)
        return Formatters.human_time(eta)

    def increment(self, add_value):
        self.current_value += add_value + self.bulgarian_constant
        self.last_increment_time = time.time()
