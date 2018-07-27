'''
'''

import json
from utils import listFilesExtension

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