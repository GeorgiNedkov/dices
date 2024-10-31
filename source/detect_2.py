import numpy as np
import cv2 as cv
import math

from source.dot import Dot
from source.isCircle import isCircle
from source.clustering import distSquare


def detect(original: cv.typing.MatLike):
    diceWidth = 40

    def crop_ring(image, crop_width, crop_height, center):
        center_y, center_x = center

        start_x = max(center_x - crop_width // 2, 0)
        start_y = max(center_y - crop_height // 2, 0)
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Crop the image
        cropped_image = image[start_y:end_y, start_x:end_x]

        return cropped_image

    ringCenter = (250, 325)
    radius = 150
    radiusSquared = radius**2
    center_y, center_x = ringCenter

    original = crop_ring(original, radius * 2, radius * 2, ringCenter)
    height, width = original.shape

    img = original.copy()
    height, width = img.shape
    center_y, center_x = (height // 2, width // 2)
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

    # [0,1,0,0,0,0 ...]
    isPixelChecked = np.zeros((height, width), dtype=np.bool)

    def findSector(point, onlyWhite):
        arr = [point]
        cluster = []
        while len(arr):
            poped = arr.pop()
            y, x = poped

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
                    cluster.append(poped)
                    isPixelChecked[y, x] = 1

                    arr.append((y, x + 1))
                    arr.append((y, x - 1))
                    arr.append((y + 1, x))
                    arr.append((y - 1, x))

        return cluster

    dots: list[Dot] = []
    for y in range(0, height):
        for x in range(0, width):
            if onlyWhite[y, x] == 255 and isPixelChecked[y, x] == 0:
                pixels = findSector((y, x), onlyWhite)
                dots.append(Dot(pixels))

    validDots = []

    for dot in dots:
        dot.calc()

    for dot in dots:
        pixelsLen = len(dot.pixels)

        if pixelsLen <= 15 or pixelsLen > 100:
            for pixel in dot.pixels:
                y, x = pixel
                onlyWhite[y, x] = 0
            continue

        if dot.w > 20 or dot.h > 20:
            for pixel in dot.pixels:
                y, x = pixel
                onlyWhite[y, x] = 0
            continue

        validDots.append(dot)

    dots = validDots
    validDots = []

    for dot in dots:
        if isCircle(dot.dimension(), onlyWhite):
            validDots.append(dot)
        else:

            for pixel in dot.pixels:
                y, x = pixel
                onlyWhite[y, x] = 0

    dots = validDots
    validDots = []

    tmpImg2 = cv.cvtColor(original, cv.COLOR_GRAY2RGB)

    length = len(dots)

    all = []
    for i in range(0, length):
        for j in range(0, length):
            dot1 = dots[i]
            dot2 = dots[j]

            cy = (dot1.cy + dot2.cy) / 2
            cx = (dot1.cx + dot2.cx) / 2
            all.append((cy, cx))

    def findSector(point, isPixelChecked, onlyWhite):
        arr = [point]
        pixels = []
        while len(arr):
            y, x = arr.pop()

            if y >= height:
                continue
            if x >= width:
                continue
            if x < 0:
                continue
            if y < 0:
                continue

            if isPixelChecked[y, x] == 0:
                if onlyWhite[y, x] == 255:
                    isPixelChecked[y, x] = 1
                    pixels.append((y, x))
                    arr.append((y, x + 1))
                    arr.append((y, x - 1))
                    arr.append((y + 1, x))
                    arr.append((y - 1, x))

        cx = 0
        cy = 0
        for p in pixels:
            cx += p[1]
            cy += p[0]

        if len(pixels) == 0:
            return (0, 0)

        cx /= len(pixels)
        cy /= len(pixels)
        return (cy, cx)

    def find_angle_between_points(p1, p2):
        y1, x1 = p1
        y2, x2 = p2
        dx = x2 - x1
        dy = y2 - y1

        angle_radians = math.atan2(dy, dx)

        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def are_opposite_angles(angle1, angle2, tolerance=20):
        angle1 = angle1 % 360
        angle2 = angle2 % 360

        difference = abs(angle1 - angle2)

        if difference > 180:
            difference = 360 - difference

        return 180 - tolerance <= difference <= 180 + tolerance

    def checkDot(point, onlyWhite, dots: list[Dot]):
        y, x = point
        roundedY = round(y)
        roundedX = round(x)

        r = diceWidth / 2

        nearDots: list[Dot] = list(
            filter(lambda dot: distSquare(dot.centerPoint, point) < r * r, dots)
        )
        # for d in nearDots:
        #     d.printInfo()

        distances = []
        if len(nearDots) == 0:
            return -1

        if len(nearDots) % 2 == 0:
            if onlyWhite[roundedY, roundedX] != 0:
                return -1
        else:
            if onlyWhite[roundedY, roundedX] != 255:
                return -1

        for dot in nearDots:
            distances.append((math.sqrt(distSquare(dot.centerPoint, point)), dot))

        distances = sorted(distances, key=lambda x: x[0])
        d1 = distances[0]
        count = 0
        sectored = [[]]
        # print(distances)
        for d2 in distances:
            if abs(d1[0] - d2[0]) < 2:
                sectored[count].append(d2)
                continue
            sectored.append([d2])
            count = 1
            d1 = d2

        countDistances = []

        for s in sectored:
            countDistances.append(len(s))

        if (
            countDistances != [1]
            and countDistances != [2]
            and countDistances != [1, 2]
            and countDistances != [4]
            and countDistances != [2, 2]
            and countDistances != [1, 4]
            and countDistances != [1, 2, 2]
            and countDistances != [2, 4]
            and countDistances != [2, 2, 2]
        ):
            if len(distances) == 4:
                countDistances = [4]
                sectored = [[distances[0], distances[1], distances[2], distances[3]]]
            if len(distances) == 5:
                countDistances = [1, 4]
                sectored = [
                    [distances[0]],
                    [distances[1], distances[2], distances[3], distances[4]],
                ]
            if len(distances) == 6:
                countDistances = [6]
                sectored = [
                    [
                        distances[0],
                        distances[1],
                        distances[2],
                        distances[3],
                        distances[4],
                        distances[5],
                    ]
                ]

        for s in sectored:
            if len(s) <= 1:
                continue
            angles = [
                find_angle_between_points(point, item[1].centerPoint) % 360
                for item in s
            ]
            countChecks = 0
            for index1, angle1 in enumerate(angles):
                check = 0
                for index2, angle2 in enumerate(angles):
                    if index2 <= index1:
                        continue
                    if are_opposite_angles(angle1, angle2):
                        check = 1

                countChecks += check
            if countChecks != len(s) / 2:
                return -1

        if countDistances == [1]:
            return 1
        if countDistances == [2]:
            return 2
        if countDistances == [1, 2]:
            return 3
        if countDistances == [4]:
            return 4
        if countDistances == [2, 2]:
            return 4
        if countDistances == [1, 4]:
            return 5
        if countDistances == [1, 2, 2]:
            return 5
        if countDistances == [2, 4]:
            return 6
        if countDistances == [2, 2, 2]:
            return 6
        if countDistances == [6]:
            return 6
        return -1

    valid = []
    for index, point in enumerate(all):
        # if index != 14:
        #     continue
        dotValue = checkDot(point, onlyWhite, dots)
        if dotValue != -1:
            valid.append((dotValue, index, point))
            color = (0, 0, 255)
            y, x = point
            roundedY = round(y)
            roundedX = round(x)
            tmpImg2 = cv.circle(tmpImg2, (roundedX, roundedY), 1, color, -1)

    tmpImg2 = cv.cvtColor(original, cv.COLOR_GRAY2RGB)
    isInvalid = False

    i = 0
    while i < len(valid):
        v1, _, p1 = valid[i]
        j = i + 1
        while j < len(valid):
            v2, _, p2 = valid[j]
            if distSquare(p1, p2) <= 16 and v1 == v2:
                valid.pop(j)
                j -= 1
            j += 1
        i += 1

    valid = sorted(valid, key=lambda x: -x[0])
    i = 0
    while i < len(valid):
        v1, _, p1 = valid[i]
        j = i + 1
        r = diceWidth / 2
        while j < len(valid):
            v2, _, p2 = valid[j]
            if distSquare(p1, p2) < r * r:
                if v1 == v2:
                    isInvalid = True
                if v1 > v2:
                    valid.pop(j)
                    j -= 1
            j += 1
        i += 1

    for index, v in enumerate(valid):
        v, i, p = valid[index]
        color = (0, 0, 255)
        y, x = p
        roundedY = round(y)
        roundedX = round(x)

        tmpImg2 = cv.circle(tmpImg2, (roundedX, roundedY), 3, color, -1)

    tmpImg2 = cv.cvtColor(original, cv.COLOR_GRAY2RGB)

    tmpValid = valid.copy()
    tmpValid = sorted(tmpValid, key=lambda x: x[2][0])

    validFiltered = set()
    popFront = True

    for d in dots:
        d.arr = []

    i = 0
    while i < len(valid):
        r = diceWidth / 2
        v, _, p = valid[i]

        def filterFunc(dot: Dot):
            return distSquare(p, dot.centerPoint) < r * r

        nearDots: list[Dot] = list(filter(filterFunc, dots))
        for d in nearDots:
            d.arr.append(i)

        i += 1

    def sortByX(d: Dot):
        return d.centerPoint[1]

    def sortByY(d: Dot):
        return d.centerPoint[0]

    dots = sorted(dots, key=sortByX)

    if len(dots[0].arr) == 1:

        validFiltered.add(valid[dots[0].arr[0]])
    if len(dots[-1].arr) == 1:

        validFiltered.add(valid[dots[-1].arr[0]])

    dots = sorted(dots, key=sortByY)
    if len(dots[0].arr) == 1:

        validFiltered.add(valid[dots[0].arr[0]])
    if len(dots[-1].arr) == 1:

        validFiltered.add(valid[dots[-1].arr[0]])

    validFiltered = list(validFiltered)
    for d in dots:
        d.arr = []

    i = 0
    while i < len(validFiltered):
        r = diceWidth / 2
        v, _, p = validFiltered[i]

        def filterFunc(dot: Dot):
            return distSquare(p, dot.centerPoint) < r * r

        nearDots: list[Dot] = list(filter(filterFunc, dots))

        for d in nearDots:
            d.arr.append(i)

        i += 1

    i = 0
    while i < len(valid):
        v, _, p = valid[i]

        def filterFunc(dot: Dot):
            return distSquare(p, dot.centerPoint) < r * r

        nearDots: list[Dot] = list(filter(filterFunc, dots))
        check = False
        for d in nearDots:
            if len(d.arr) != 0:
                check = True
        if check:
            valid.pop(i)
            continue

        i += 1

    valid = valid + validFiltered

    for index, v in enumerate(valid):
        v, i, p = valid[index]
        color = (0, 0, 255)
        y, x = p
        roundedY = round(y)
        roundedX = round(x)

        tmpImg2 = cv.circle(tmpImg2, (roundedX, roundedY), 3, color, -1)

    result = list(
        map(
            lambda v: f"{v[0]}",
            valid,
        )
    )

    return {
        "image": np.concatenate((original, img), axis=0),
        "json": {"isValid": not isInvalid, "value": result},
    }
