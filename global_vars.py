'''
'''

import json
from utils import listFilesExtension
from collections import namedtuple


SpawnUnit = namedtuple('SpawnUnit', ['unitType', 'row', 'col', 'numPlayerList'])
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
    loadHeroData()
    loadAbilityData()
    loadMonsterData()
    loadItemData()

    global numPlayersInScenario
    numPlayersInScenarion = 0

def setNumPlayersInScenario(value):
    global numPlayersInScenario
    numPlayersInScenario = value

def loadHeroData(dataFile='hero_data.json'):
    global heroDataJson

    heroDataJson = {}
    with open(dataFile, 'r') as infile:
        heroDataJson = json.load(infile)

def loadAbilityData(dataFile='abilities.json'):
    global abilityDataJson

    abilityDataJson = {}
    with open(dataFile, 'r') as infile:
        abilityDataJson = json.load(infile)

def loadItemData(dataFile='items.json'):
    global itemDataJson

    itemDataJson = {}
    with open(dataFile, 'r') as infile:
        itemDataJson = json.load(infile)

def loadMonsterData(dirPath='monster_data', deckFile='monster_deck.json'):
    global monsterDataJson
    global monsterDeckDataJson

    monsterDataJson = {}
    files = listFilesExtension(dirPath, ".json")
    for file in files:
        with open(file, 'r') as infile:
            monsterDataJson = { **monsterDataJson, **json.load(infile) }

    monsterDeckDataJson = {}
    with open(deckFile, 'r') as infile:
        monsterDeckDataJson = json.load(infile)

init()
