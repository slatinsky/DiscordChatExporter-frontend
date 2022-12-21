import time

class Progress:
    def __init__(self, objects, name=''):
        self.total = len(objects)
        self.increments = max(round(self.total / 100), 1)
        self.iteration = 0
        self.name = name
        self.last_print_time = 0

    def increment(self):
        self.iteration += 1

        should_print = self.total > 0 and self.iteration % self.increments == 0 or self.last_print_time + .1 < time.time()
        if should_print:
            print("  ", self.name, self.iteration, "/", self.total, '(' + str(round(self.iteration / self.total * 100)) + '%)', end="\r") # print progress
            self.last_print_time = time.time()

    def finish(self, msg=None):
        if msg:
            print("  ", msg)
        elif self.name != '':
            print("  ", self.name, "done                                     ")
        else:
            print("  ", "done                                     ")

