import math


def w_h_ofClusters(points1, points2):
    minX = 999999
    minY = 999999
    maxX = 0
    maxY = 0

    for p in points1:
        if minX >= p[1]:
            minX = p[1]
        if minY >= p[0]:
            minY = p[0]
        if maxX <= p[1]:
            maxX = p[1]
        if maxY <= p[0]:
            maxY = p[0]

    for p in points2:
        if minX >= p[1]:
            minX = p[1]
        if minY >= p[0]:
            minY = p[0]
        if maxX <= p[1]:
            maxX = p[1]
        if maxY <= p[0]:
            maxY = p[0]

    w = maxX - minX
    h = maxY - minY

    return [w, h]


def distSquare(p1, p2):
    return (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])


def minDistSquare_ofClusters(points1, points2):
    minDist = 99999
    for point1 in points1:
        for point2 in points2:
            dist = distSquare(point1, point2)
            if dist < minDist:
                minDist = dist

    return minDist


# sectorDimensions = [y, x, h, w, cy, cx]
def clustering(sectorDimensions, spaceBetweenDotsMax: int, diceWidthMax: int):
    clusters = []

    for dimension in sectorDimensions:
        y, x, h, w, cy, cx = dimension
        if w == 0:
            continue
        if h == 0:
            continue
        clusters.append([cy, cx, dimension])

    clusters = [[x] for x in clusters]

    for spaceBetweenDots in range(1, spaceBetweenDotsMax + 1):
        for diceWidth in range(spaceBetweenDotsMax, diceWidthMax + 1):
            clusters = sorted(clusters, key=lambda a: a[0][0], reverse=True)
            clusters = sorted(clusters, key=lambda a: len(a), reverse=True)
            i = 0
            while i != len(clusters):
                points1 = clusters[i]
                j = i + 1

                while j != len(clusters):
                    points2 = clusters[j]
                    minDist = minDistSquare_ofClusters(points1, points2)
                    w, h = w_h_ofClusters(points1, points2)
                    if (
                        minDist < spaceBetweenDots * spaceBetweenDots
                        and w < diceWidth
                        and h < diceWidth
                    ):
                        [(lambda p: clusters[i].append(p))(p) for p in clusters.pop(j)]
                    else:
                        j = j + 1

                i = i + 1

    i = 0
    while i != len(clusters):
        points1 = clusters[i]
        j = i + 1

        while j != len(clusters):
            points2 = clusters[j]
            w, h = w_h_ofClusters(points1, points2)
            if w < diceWidth and h < diceWidth:
                [(lambda p: clusters[i].append(p))(p) for p in clusters.pop(j)]
            else:
                j = j + 1

        i = i + 1

    return clusters
