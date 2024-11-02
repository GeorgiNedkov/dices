class Dot:
    pixels: list
    cy = 0
    cx = 0
    x = 0
    y = 0
    w = 0
    h = 0
    index = 0

    arr: list

    def __init__(self, pixels):
        self.pixels = pixels
        self.arr = []

    def calc(self):
        if len(self.pixels) == 0:
            return

        cx = 0
        cy = 0
        pixelsCount = 0
        xmin = 999999
        ymin = 999999
        xmax = -1
        ymax = -1

        for pixel in self.pixels:
            y, x = pixel
            pixelsCount += 1
            cx += x
            cy += y
            if ymin > y:
                ymin = y
            if ymax < y:
                ymax = y
            if xmin > x:
                xmin = x
            if xmax < x:
                xmax = x

        self.x = xmin
        self.y = ymin
        self.w = xmax - xmin + 1
        self.h = ymax - ymin + 1
        self.cx = cx / pixelsCount
        self.cy = cy / pixelsCount

    @property
    def centerPoint(self):
        return (self.cy, self.cx)

    def dimension(self):
        return (self.y, self.x, self.h, self.w, self.cy, self.cx)

    def printInfo(self):
        print(f"Dot Center Point: {self.centerPoint}")
