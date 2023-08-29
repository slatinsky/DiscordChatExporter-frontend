import functools
import time

print = functools.partial(print, flush=True)

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def change_name(self, name):
        self.name = name

    def __exit__(self, type, value, traceback):
        print(f'[{self.name}] took {round(time.time() - self.tstart, 2)} seconds')