class Progress:
    def __init__(self, objects, name=''):
        self.total = len(objects)
        self.increments = max(round(self.total / 100), 1)
        self.iteration = 0
        self.name = name

    def increment(self):
        self.iteration += 1
        if self.total > 0 and self.iteration % self.increments == 0:
            print("  ", self.name, self.iteration, "/", self.total, '(' + str(round(self.iteration / self.total * 100)) + '%)', end="\r") # print progress

    def finish(self):
        if self.name != '':
            print("  ", self.name, "done                                     ")
        else:
            print("  ", "done                                     ")

