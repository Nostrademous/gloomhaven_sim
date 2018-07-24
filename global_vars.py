'''
'''

import json

def init():
    global abilityDataJson
    global heroDataJson
    global itemDataJson
    abilityDataJson = loadAbilityData()
    heroDataJson = loadHeroData()
    itemDataJson = loadItemData()
    
def loadHeroData(dataFile='hero_data.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadAbilityData(dataFile='abilities.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadItemData(dataFile='items.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)
