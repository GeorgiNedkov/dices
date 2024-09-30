import numpy as np
import cv2 as cv
from pathlib import Path
import math

from side import Side
from dice import Dice

from clustering import clustering, distSquare

images = [
    "2024-05-07_16-17-38_original",
    "2024-05-07_21-01-54_original",
    "2024-05-08_10-09-13_original",
    "2024-05-07_18-23-50_original",
    "2024-05-09_04-54-21_original",
    "2024-05-08_08-52-20_original",
    "2024-05-08_09-12-47_original",
    "2024-05-07_18-44-44_original",
    "2024-05-09_06-02-42_original",
    "2024-05-09_05-55-43_original",
    "2024-05-08_07-40-01_original",
    "2024-05-07_16-07-07_original",
    "2024-05-09_09-34-35_original",
    "2024-05-09_08-10-37_original",
    "2024-05-09_09-17-10_original",
    "2024-05-08_02-57-30_original",
    "2024-05-09_09-34-35_original",
]

for imageName in images:
    writeToFile = True
    outputFolder = f"../data/output/{imageName}"
    Path(outputFolder).mkdir(parents=True, exist_ok=True)
    diceWidth = 35

    original = cv.imread(f"../data/original/{imageName}.png")
    assert original is not None, "file could not be read"

    img = original.copy()

    height, width, channels = img.shape
    ringCenter = (250, 325)
    radius = 150

    for y in range(0, height):
        for x in range(0, width):
            dist = distSquare(ringCenter, (y, x))
            if dist > radius * radius:
                img[y, x] = [0, 0, 0]

    if writeToFile:
        cv.imwrite(f"../data/out/{imageName}.png", img)
        cv.imwrite(f"{outputFolder}/cutout.png", img)

    radAndSomeMore = radius + 100
    crop = img[
        ringCenter[0] - radAndSomeMore : ringCenter[0] + radAndSomeMore,
        ringCenter[1] - radAndSomeMore : ringCenter[1] + radAndSomeMore,
    ]

    onlyWhite = img.copy()

    for y in range(0, height):
        for x in range(0, width):
            if onlyWhite[y, x, 0] <= 240:
                onlyWhite[y, x] = [0, 0, 0]
            else:
                onlyWhite[y, x] = [255, 255, 255]

    if writeToFile:
        cv.imwrite(f"{outputFolder}/whitePixels.png", onlyWhite)

    # %%
    # [ 254, 100, 12, ...]
    sectorsCounts = [0]
    # [0,1,0,4,4,4,0,0,0,1...]
    imgSectorMap = np.zeros((height, width), dtype=np.uint8)
    # [0,1,0,0,0,0 ...]
    isPixelChecked = np.zeros((height, width), dtype=np.uint8)
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
                if onlyWhite[y, x, 0] == 255:
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
            if onlyWhite[y, x, 0] >= 254 and imgSectorMap[y, x] == 0:
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

        if sector <= 20 or sector >= 100:
            for x_y_sector_arr in sectorsByPixels:
                s = x_y_sector_arr[2]
                if s == index:
                    y = x_y_sector_arr[0]
                    x = x_y_sector_arr[1]
                    onlyWhite[y, x] = [0, 0, 0]
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
            sectorDimensions[index] = [ymin, xmin, h, w, cy, cx]

    def myFunc(x):
        if x[2] == 0:
            return False
        if x[3] == 0:
            return False
        return True

    sectorDimensions = list(filter(myFunc, sectorDimensions))

    if writeToFile:
        cv.imwrite(f"{outputFolder}/dots.png", onlyWhite)

    spaceBetweenDots = math.floor(diceWidth / 2)
    sidesClusters = clustering(sectorDimensions, spaceBetweenDots, diceWidth)
    diceClusters = clustering(sectorDimensions, spaceBetweenDots, diceWidth + 10)

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
    index = 0
    for dice in dices:
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

    if writeToFile:
        tmpImage = np.concatenate((original, tmpImage), axis=0)
        cv.imwrite(f"{outputFolder}/score.png", tmpImage)
