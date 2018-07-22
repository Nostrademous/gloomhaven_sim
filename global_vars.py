'''
'''

import json

def init():
    global abilityDataJson
    global heroDataJson
    abilityDataJson = loadAbilityData()
    heroDataJson = loadHeroData()
    
def loadHeroData(dataFile='hero_data.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)

def loadAbilityData(dataFile='abilities.json'):
    with open(dataFile, 'r') as infile:
        return json.load(infile)