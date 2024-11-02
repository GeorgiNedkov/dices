from source.dot import Dot


class Dice:
    dots: list[Dot]
    center: list

    def __init__(self, dots: list[Dot], point: list):
        self.dots = dots
        self.center = point

    @property
    def value(self):
        return len(self.dots)
