import numpy as np
import cv2 as cv
from pathlib import Path
import math

from source.side import Side
from source.dice import Dice

from source.clustering import clustering, distSquare

from source.images import images, imagesWrong

count = 0
for imageName in images:
    count += 1
    print(count)
    writeToFile = True
    outputFolder = f"./data/output/{imageName}"
    Path(outputFolder).mkdir(parents=True, exist_ok=True)
    diceWidth = 35

    original = cv.imread(f"./newData/{imageName}", cv.IMREAD_GRAYSCALE)
    assert original is not None, "file could not be read"

    img = original.copy()

    height, width = img.shape
    ringCenter = (250, 325)
    radius = 150
    radiusSquared = radius**2
    center_y, center_x = (250, 325)
    Y, X = np.ogrid[:height, :width]
    distance_from_center = (X - center_x) ** 2 + (Y - center_y) ** 2
    mask = distance_from_center >= radiusSquared
    img[mask] = 0

    edges = cv.Canny(img, 100, 100)
    cv.imwrite(f"{outputFolder}/edges.png", edges)

    onlyWhite = img.copy()

    non_white_mask = onlyWhite <= 250
    reverse_mask = ~non_white_mask
    # Set all non-white pixels to black (0)
    onlyWhite[non_white_mask] = 0
    onlyWhite[reverse_mask] = 255

    if writeToFile:
        cv.imwrite(f"{outputFolder}/whitePixels.png", onlyWhite)

    # [ 254, 100, 12, ...]
    sectorsCounts = [0]
    # [0,1,0,4,4,4,0,0,0,1...]
    imgSectorMap = np.zeros((height, width), dtype=np.uint16)
    # [0,1,0,0,0,0 ...]
    isPixelChecked = np.zeros((height, width), dtype=np.bool)
    # [[y,x, sector], ...]
    sectorsByPixels = []

    def findSector(startingY, startingX, number):
        global onlyWhite, sectorsByPixels, imgSectorMap, sectorsCounts
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

    for y in range(0, height):
        for x in range(0, width):
            if onlyWhite[y, x] >= 254 and imgSectorMap[y, x] == 0:
                sectorsCounts.append(0)
                findSector(y, x, len(sectorsCounts) - 1)

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

    if writeToFile:
        cv.imwrite(f"{outputFolder}/dots.png", onlyWhite)

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

            tmpOutText += " IN "

    if writeToFile:
        tmpImage = np.concatenate((original, tmpImage), axis=0)
        cv.imwrite(f"{outputFolder}/score.png", tmpImage)

    tmpImg = np.zeros((500, 500, 3), dtype=np.uint8)
    for p in sidesClusters[1]:
        tmpImg = cv.circle(
            tmpImg, (math.floor(p[1]), math.floor(p[0])), 5, (255, 255, 255), -1
        )

    tmpImg = np.zeros((height, width, 3), dtype=np.uint8)
    for dimension in sectorDimensions:
        y, x, h, w, cy, cx = dimension
        if w == 0:
            continue
        if h == 0:
            continue

        padding = 3
        for i in range(math.floor(y - padding), math.floor(y + h + padding + 1)):
            for j in range(math.floor(x - padding), math.floor(x + w + padding + 1)):
                tmpImg[i, j] = original[i, j].copy()

    if writeToFile:
        cv.imwrite(f"{outputFolder}/dices_colored.png", tmpImg)

    img = cv.putText(
        img,
        tmpOutText,
        (20, 200),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2,
        cv.LINE_4,
    )

    if writeToFile:
        cv.imwrite(f"{outputFolder}/aaaaaaaaaa.png", img)
