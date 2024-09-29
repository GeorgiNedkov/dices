import numpy as np
import math


def isCircle(dimension, original):
    errorLevel = 0
    y, x, h, w, cy, cx = dimension
    padding = 0
    tmpImg = original[
        y - padding : y + h + padding, x - padding : x + w + padding
    ].copy()
    theight, twidth, _ = tmpImg.shape
    for i in range(0, theight):
        for j in range(0, twidth):
            if tmpImg[i, j][0] > 250:
                tmpImg[i, j] = np.array((255, 255, 255))
            else:
                tmpImg[i, j] = np.array((0, 0, 0))

    xmin = 999999
    ymin = 999999
    xmax = -1
    ymax = -1

    for i in range(0, theight):
        for j in range(0, twidth):
            if tmpImg[i, j][0] == 255:
                if ymin > i:
                    ymin = i
                if ymax < i:
                    ymax = i
                if xmin > j:
                    xmin = j
                if xmax < j:
                    xmax = j

    w = xmax - xmin
    h = ymax - ymin
    cx = xmin + w / 2
    cy = ymin + h / 2
    # print("w: ", w, " h: ", h, " cx: ", cx, " cy: ", cy)

    if w < 6 or h < 6:
        return 999

    if w - h < -2 or w - h > 2:
        return 999

    minDistances = [99999, 99999]
    for i in range(0, theight):
        for j in range(0, twidth):
            if tmpImg[i, j][0] != 255:
                dist = (cy - i) * (cy - i) + (cx - j) * (cx - j)
                if minDistances[0] > dist:
                    minDistances[0] = dist
                    minDistances = sorted(minDistances, reverse=True)

    maxDistances = list(map(lambda x: 0, minDistances))
    for i in range(0, theight):
        for j in range(0, twidth):
            if tmpImg[i, j][0] == 255:
                dist = (cy - i) * (cy - i) + (cx - j) * (cx - j)
                if maxDistances[0] < dist:
                    maxDistances[0] = dist
                    maxDistances = sorted(maxDistances, reverse=False)

    maxDistances = list(map(lambda x: math.sqrt(x), maxDistances))
    minDistances = list(map(lambda x: math.sqrt(x), minDistances))

    errorLevel = sum(maxDistances) / len(maxDistances) - (sum(minDistances)) / len(
        minDistances
    )

    return errorLevel
