'''
'''

import json
from utils import listFilesExtension
from collections import namedtuple

Location = namedtuple('Location', ['row', 'col'])
def rotateLocationLeft(loc, num_times=1):
    """Given a hex coordinate (x, y) return the coordinate of hex when rotated 60° around the origin.
    """
    for i in range(num_times):
        loc = Location((loc[0] - 3 * loc[1]) >> 1, (loc[0] + loc[1]) >> 1)
    return loc

def calculateTrapDamage(scenarioLevel):
    return scenarioLevel + 2

def calculateHazardDamage(scenarioLevel):
    return int(self.calculateTrapDamage(scenarioLevel)/2)

def calculateMonsterLevel(scenarioLevel):
    return scenarioLevel

def calculateBonusExperience(scenarioLevel):
    return (scenarioLevel * 2) + 4

def init():
    global abilityDataJson
    global heroDataJson
    global itemDataJson

    abilityDataJson = loadAbilityData()
    heroDataJson = loadHeroData()
    itemDataJson = loadItemData()

    loadMonsterData()

def loadHeroData(dataFile='hero_data.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadAbilityData(dataFile='abilities.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadItemData(dataFile='items.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadMonsterData(dirPath='monster_data'):
    global monsterDataJson

    monsterDataJson = {}
    files = listFilesExtension(dirPath, ".json")
    for file in files:
        with open(file, 'r') as infile:
            monsterDataJson = { **monsterDataJson, **json.load(infile) }

init()
