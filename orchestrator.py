"""
"""

import character as hero
import scenario

def loadScenario(scenario):
    print("[loadScenario] - IMPLEMENT")

def loadPartyIntoScenario(scenario, listParty):
    print("[loadPartyIntoScenario] - IMPLEMENT")
    for hero in listParty:
        scenario.addPlayer(hero)