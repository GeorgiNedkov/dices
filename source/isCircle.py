import numpy as np
import math
import cv2 as cv


def isCircle(dimension, original: cv.typing.MatLike):
    errorLevel = 0
    y, x, h, w, cy, cx = dimension
    padding = 0

    tmpImg = original[
        y - padding : y + h + padding, x - padding : x + w + padding
    ].copy()

    theight, twidth = tmpImg.shape

    isPixelChecked = np.zeros((theight, twidth), dtype=np.uint8)

    findSector(
        math.floor(theight / 2),
        math.floor(twidth / 2),
        theight,
        twidth,
        isPixelChecked,
        tmpImg,
    )

    xmin = 999999
    ymin = 999999
    xmax = -1
    ymax = -1

    count = 0
    cx = 0
    cy = 0
    for i in range(0, theight):
        for j in range(0, twidth):
            if isPixelChecked[i, j] == 1:
                count += 1
                cx += j
                cy += i
                if ymin > i:
                    ymin = i
                if ymax < i:
                    ymax = i
                if xmin > j:
                    xmin = j
                if xmax < j:
                    xmax = j

    if count == 0:
        return False

    w = xmax - xmin
    h = ymax - ymin
    cx = (cx / count) + 0.5
    cy = (cy / count) + 0.5

    # print("w: ", w, " h: ", h, " cx: ", cx, " cy: ", cy)

    if w < 5 or h < 5:
        return False

    if w - h < -3 or w - h > 3:
        return False

    minDistances = [99999, 99999]
    for i in range(0, theight):
        for j in range(0, twidth):
            if isPixelChecked[i, j] == 0:
                tmpX = j + 1 if j > cy else j
                tmpY = i + 1 if i > cy else i

                dist = (cy - tmpY) * (cy - tmpY) + (cx - tmpX) * (cx - tmpX)
                if minDistances[0] > dist:
                    minDistances[0] = dist
                    minDistances = sorted(minDistances, reverse=True)

    maxDistances = list(map(lambda x: 0, minDistances))
    for i in range(0, theight):
        for j in range(0, twidth):
            if isPixelChecked[i, j] == 1:
                # find nearest point of the pixel
                tmpX = j + 1 if j + 0.5 < cx else j + 0.5 if j + 0.5 == cx else j
                tmpY = i + 1 if i + 0.5 < cx else i + 0.5 if i + 0.5 == cx else i

                dist = (cy - tmpY) * (cy - tmpY) + (cx - tmpX) * (cx - tmpX)
                if maxDistances[0] < dist:
                    maxDistances[0] = dist
                    maxDistances = sorted(maxDistances, reverse=False)

    maxDistances = list(map(lambda x: math.sqrt(x), maxDistances))
    minDistances = list(map(lambda x: math.sqrt(x), minDistances))

    errorLevel = sum(maxDistances) / len(maxDistances) - (sum(minDistances)) / len(
        minDistances
    )

    # print(errorLevel)
    return errorLevel <= 0


def findSector(startingY, startingX, height, width, isPixelChecked, onlyWhite):
    arr = [[startingY, startingX]]
    while len(arr):
        poped = arr.pop()
        y = poped[0]
        x = poped[1]

        if y == height:
            continue
        if x == width:
            continue
        if x < 0:
            continue
        if y < 0:
            continue

        if isPixelChecked[y, x] == 0:
            if onlyWhite[y, x] == 255:
                isPixelChecked[y, x] = 1

                arr.append([y, x + 1])
                arr.append([y, x - 1])
                arr.append([y + 1, x])
                arr.append([y - 1, x])
