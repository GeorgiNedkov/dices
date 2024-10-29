import numpy as np
import cv2 as cv
import math

from source.side import Side
from source.dice import Dice

from source.clustering import clustering, distSquare


def detect(original: cv.typing.MatLike):
    diceWidth = 35

    img = original.copy()

    height, width = img.shape
    ringCenter = (250, 325)
    radius = 150
    radiusSquared = radius**2
    center_y, center_x = ringCenter
    Y, X = np.ogrid[:height, :width]
    distance_from_center = (X - center_x) ** 2 + (Y - center_y) ** 2
    mask = distance_from_center >= radiusSquared
    img[mask] = 0

    onlyWhite = img.copy()

    non_white_mask = onlyWhite <= 250
    reverse_mask = ~non_white_mask
    # Set all non-white pixels to black (0)
    onlyWhite[non_white_mask] = 0
    onlyWhite[reverse_mask] = 255

    # [ 254, 100, 12, ...]
    sectorsCounts = [0]
    # [0,1,0,4,4,4,0,0,0,1...]
    imgSectorMap = np.zeros((height, width), dtype=np.uint16)
    # [0,1,0,0,0,0 ...]
    isPixelChecked = np.zeros((height, width), dtype=np.bool)
    # [[y,x, sector], ...]
    sectorsByPixels = []

    for y in range(0, height):
        for x in range(0, width):
            if onlyWhite[y, x] >= 254 and imgSectorMap[y, x] == 0:
                sectorsCounts.append(0)
                startingY, startingX, number = (y, x, len(sectorsCounts) - 1)
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
                            imgSectorMap[y, x] = number
                            sectorsByPixels.append([y, x, number])
                            sectorsCounts[number] = sectorsCounts[number] + 1

                            arr.append([y, x + 1, number])
                            arr.append([y, x - 1, number])
                            arr.append([y + 1, x, number])
                            arr.append([y - 1, x, number])

    validDots = []
    validPixels = []

    # y,x, height, width, cy, cx
    sectorDimensions = []

    for index, sector in enumerate(sectorsCounts):
        xmin = 999999
        ymin = 999999
        xmax = -1
        ymax = -1
        sectorDimensions.append([0, 0, 0, 0, 0, 0])
        if sector == 0:
            continue

        if sector <= 15 or sector >= 100:
            for x_y_sector_arr in sectorsByPixels:
                s = x_y_sector_arr[2]
                if s == index:
                    y = x_y_sector_arr[0]
                    x = x_y_sector_arr[1]
                    onlyWhite[y, x] = 0
        else:
            validDots.append([])
            for x_y_sector_arr in sectorsByPixels:
                s = x_y_sector_arr[2]
                if s == index:
                    y = x_y_sector_arr[0]
                    x = x_y_sector_arr[1]
                    validPixels.append([y, x])
                    validDots[len(validDots) - 1].append([y, x])
                    if ymin > y:
                        ymin = y
                    if ymax < y:
                        ymax = y
                    if xmin > x:
                        xmin = x
                    if xmax < x:
                        xmax = x
            w = xmax - xmin + 1
            h = ymax - ymin + 1
            cx = xmin + w / 2
            cy = ymin + h / 2

            if w > 20 or h > 20:
                for x_y_sector_arr in sectorsByPixels:
                    s = x_y_sector_arr[2]
                    if s == index:
                        y = x_y_sector_arr[0]
                        x = x_y_sector_arr[1]
                        onlyWhite[y, x] = 0
            else:
                sectorDimensions[index] = [ymin, xmin, h, w, cy, cx]

    def filterEmpty(x):
        if x[2] == 0:
            return False
        if x[3] == 0:
            return False
        return True

    sectorDimensions = list(filter(filterEmpty, sectorDimensions))

    spaceBetweenDots = math.floor(diceWidth / 2)
    sidesClusters = clustering(sectorDimensions, spaceBetweenDots, diceWidth)
    diceClusters = clustering(sectorDimensions, spaceBetweenDots, diceWidth + 20)

    dices: list[Dice] = list(map(lambda x: Dice(), range(len(diceClusters))))

    for index, diceCluster in enumerate(diceClusters):
        for index2, sideCluster in enumerate(sidesClusters):
            check = False
            for p in diceCluster:
                for p2 in sideCluster:
                    if p[0] == p2[0] and p[1] == p2[1]:
                        check = True
                        break
            if check:
                side = Side(original)
                side.dimensions = list(map(lambda x: x[2], sideCluster))
                dices[index].sides.append(side)

    for dice in dices:
        if len(dice.sides) == 1:
            dice.isValid = dice.sides[0].isValid
            dice.value = dice.sides[0].value
            continue
        if len(dice.sides) > 1:
            countValid = 0

            validSides: list[Side] = []
            invalidSides: list[Side] = []
            for side in dice.sides:
                if side.isValid:
                    validSides.append(side)
                    continue
                else:
                    invalidSides.append(side)
            if len(validSides) != 1:
                dice.isValid = False
                dice.value = -1
                continue
            validSide = validSides[0]
            check = True
            for invalidSide in invalidSides:
                centerOFImage: list[float] = [height / 2, width / 2]
                d1 = distSquare(centerOFImage, invalidSide.center)
                d2 = distSquare(centerOFImage, validSide.center)
                if d2 < d1:
                    check = False

            if check:
                dice.isValid = True
                dice.value = validSide.value

    tmpImage = original.copy()
    tmpOutText = ""
    for index, dice in enumerate(dices):
        cy, cx = dice.center
        rcx = math.floor(cx)
        rcy = math.floor(cy)
        tmpImage = cv.circle(tmpImage, (rcx, rcy), 40, (0, 255, 255, 0.1))
        if dice.isValid:
            cv.putText(
                tmpImage,
                f"{dice.value}",
                (rcx, rcy),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                2,
                cv.LINE_4,
            )
            tmpOutText += f" {dice.value} "
        else:
            cv.putText(
                tmpImage,
                f'{"IN"}',
                (rcx, rcy),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                2,
                cv.LINE_4,
            )

    isValid = True
    result: list[int] = list()
    for dice in dices:
        if not dice.isValid:
            isValid = False

    if len(dices) != 3:
        isValid = False

    result = list(
        map(
            lambda dice: f"{dice.value}" if dice.isValid else f"invalid",
            dices,
        )
    )

    return {
        "image": np.concatenate((original, tmpImage), axis=0),
        "json": {"isValid": isValid, "value": result},
    }
