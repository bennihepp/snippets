import persistent

class Model(persistent.Persistent):

    def __init__(self, data):
        self.data = data
        self.__private = data

    def private(self):
        return self.__private

    @property
    def x(self):
        return self.data
    @x.setter
    def x(self, data):
        self.data = data

