from source.functions import isCircle


class Side:
    dimensions = []
    __isValid = 0

    def __init__(self, original):
        self.original = original

    @property
    def isValid(self):
        if self.__isValid == 1:
            return True

        if self.__isValid == -1:
            return False

        check = True
        for dimension in self.dimensions:
            errorLevel = isCircle(dimension, self.original)
            if errorLevel >= 0.9:
                check = False

        if check:
            self.__isValid = 1
        else:
            self.__isValid = -1

        return check

    @property
    def center(self):
        cxs = list(map(lambda x: x[5], self.dimensions))
        cys = list(map(lambda x: x[4], self.dimensions))
        cx = sum(cxs) / len(cxs)
        cy = sum(cys) / len(cys)
        return [cy, cx]

    @property
    def value(self):
        return len(self.dimensions)
