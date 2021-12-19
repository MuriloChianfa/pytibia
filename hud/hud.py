import numpy as np
import cv2
y = np.array([
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    480, 506,
    960, 986,
    1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466
])
x = np.arange(y.size)

allBlack = np.zeros(y.size)
hudWidth = 480


def getCreaturesBars(blackPixels):
    blackPixelsIndexes = np.nonzero(blackPixels == 0)[0]
    noBlackPixels = blackPixelsIndexes.size == 0
    if noBlackPixels:
        return np.array([])
    x = np.broadcast_to(blackPixelsIndexes, (y.size, blackPixelsIndexes.size))
    x = np.transpose(x)
    z = np.add(x, y)
    pixelsColorsIndexes = np.take(blackPixels, z)
    g = (pixelsColorsIndexes == allBlack).all(1)
    possibleCreatures = np.nonzero(g)[0]
    hasNoCreatures = possibleCreatures.size == 0
    if hasNoCreatures:
        return np.array([])
    creatures = np.take(blackPixelsIndexes, possibleCreatures)
    creatures = np.array(
        list(map(lambda i: [i % hudWidth, i // hudWidth], creatures)))
    return creatures


creaturesNamesHashes = {
    "Cyclops": np.array(cv2.imread('hud/images/monsters/Cyclops.png', cv2.IMREAD_GRAYSCALE)),
    "Frost Dragon Hatchling": np.array(cv2.imread('hud/images/monsters/Frost Dragon Hatchling.png', cv2.IMREAD_GRAYSCALE)),
    "Rat": np.array(cv2.imread('hud/images/monsters/Rat.png', cv2.IMREAD_GRAYSCALE)),
}


def getCreatures_perf(hud, creaturesBars, battleListCreatures):
    hashImgWidth = 27
    battleListMonstersCount = battleListCreatures.size
    # obtaining a flattened contigous mess array of each creatures bars in 3d array
    # creaturesBarsHashes = np.array([hud[creature[1] - 13:creature[1] - 13 + 11,
    #                                creature[0]: creature[0] + hashImgWidth] for creature in creaturesBars])
    creaturesBarsHashes = np.array(
        list(map(lambda creature: np.ravel(hud[creature[1] - 13:creature[1] - 13 + 11,
                                               creature[0]: creature[0] + hashImgWidth]), creaturesBars)))
    # converting each pixel with color 113(color inside letters) to black
    creaturesBarsHashes = np.where(
        creaturesBarsHashes == 113, 0, creaturesBarsHashes)
    # converting each black pixel to 1
    creaturesBarsHashes = np.where(creaturesBarsHashes == 0, 1, 0)
    # obtaining a flattened contigous clean array of each creature in battle list
    battleListMonstersHashes = np.array(
        list(map(lambda creature: np.ravel(creaturesNamesHashes[creature["name"]]), battleListCreatures)))
    # battleListMonstersHashes = np.array(
    # [np.ravel(creaturesNamesHashes[creature["name"]]) for creature in battleListCreatures])
    # converting white pixels to 1
    battleListMonstersHashes = np.where(battleListMonstersHashes == 255, 1, 0)
    left = np.repeat(creaturesBarsHashes, battleListMonstersCount, axis=0)
    left = np.array(np.vsplit(left, battleListMonstersCount))
    right = np.broadcast_to(battleListMonstersHashes,
                            (creaturesBarsHashes.shape[0],
                             battleListMonstersCount,
                             battleListMonstersHashes.shape[1]))
    z = np.add(left, right)
    z = np.all(z == 1, axis=2)
    z = np.where(z, 1, 0)
    z = z - 1
    z = z.flatten()
    creatures = np.take(battleListCreatures, z)
    return creatures


def getCreatures(hud, creaturesBars, battleListCreatures):
    hasUniqueMonster = len(battleListCreatures) == 1
    if hasUniqueMonster:
        (x, y) = creaturesBars[0]
        return np.array([[battleListCreatures[0], [x, y]]], dtype=object)
    creatures = np.array([], dtype=object)
    for creatureBar in creaturesBars:
        (x, y) = creatureBar
        for creatureNameHash in creaturesNamesHashes:
            creatureMess = hud[y - 13: y - 13 + 11, x: x + 27]
            creatureMess = np.where(
                creatureMess == 113, 0, creatureMess)
            creatureMess = np.where(creatureMess != 0, 255, creatureMess)
            creatureMessFlattened = creatureMess.flatten()
            creatureHashFlattened = creaturesNamesHashes[creatureNameHash].flatten(
            )
            creatureBlackPixelsIndexes = np.nonzero(
                creatureHashFlattened == 0)[0]
            blackPixels = np.take(creatureMessFlattened,
                                  creatureBlackPixelsIndexes)
            creatureDidMatch = np.all(blackPixels == 0)
            if creatureDidMatch:
                creatures = np.append(
                    creatures, np.array([creatureNameHash, [x, y]], dtype=object))
    return creatures
