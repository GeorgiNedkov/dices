from source.side import Side


class Dice:
    sides: list[Side]
    isValid: bool = False
    value: int = -1

    def __init__(self):
        self.sides = []

    @property
    def center(self):
        cxs = list(map(lambda side: side.center[1], self.sides))
        cys = list(map(lambda side: side.center[0], self.sides))
        cx = sum(cxs) / len(cxs)
        cy = sum(cys) / len(cys)
        return [cy, cx]
