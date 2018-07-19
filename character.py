'''
    Gloomhaven Characters have the following attributes:
    
        # Stage 1 implementation tracking
        Name: (string literal)
        Player: (string literal of player owning this hero)
        Type: Brute, Cragheart, Tinkerer, Scoundrel, Spellweaver, Mindthief
        Level: 1 to 9 (default 1)
        Current Health: (default 0)
        Max Health: (default 0)
        XP: (default 0)
        Gold: (default 0)
        Quest: (integer literal)
        Checkmarks: (default 0, integer literal) # 3 checkmarks == 1 perk
        
        # Stage 2 implementation tracking
        IsRetired: (default False)
        IsExhausted: (default False)
        
        # Stage 3 implementation tracking
        Effects: list() #immobilized, poisoned, wounded, etc.
        Spawns: list(class units.py)
        
        # Stage 4 implementation tracking
        Items: list(class items.py)
        AMD (Attack Modifier Deck): class(attack_mod_deck.py)
        
        # Stage 5 implementation tracking
        AbilityCards: list(class abilityCards.py)
        Perks: list(class perks.py)
        
        # Stage 6 implementation tracking
        Location: (class location.py) - Scenario # + hex-grid
        Scenario Mission: (class scenario_mission.py)
        
        # FUTURE TODO - maybe more stuff needed
'''

import json
import global_vars as gv

valid_types = ['Brute', 'Cragheart', 'Tinkerer', 'Scoundrel', 'Spellweaver', 'Mindthief']

class Character():
    def __init__(self, name, type, owner='<UNKNOWN>', level=1, xp=0, gold=30, quest=0, checkmarks=0):
        assert type in valid_types
        
        self.data = {}
        self.data['name'] = name
        self.data['type'] = type
        self.data['owner'] = owner
        self.data['level'] = level
        self.data['xp'] = xp
        self.data['gold'] = gold
        self.data['quest'] = quest # for tracking retirement conditions
        self.data['checkmarks'] = checkmarks

        if gv.heroDataJson:
            self.data['curr_health'] = gv.heroDataJson[type.capitalize()]['Health'][str(level)]
            self.data['max_health'] = self.data['curr_health']
            self.data['deck_size'] = gv.heroDataJson[type.capitalize()]['DeckSize']

        self.data['retired'] = False
        self.data['exhausted'] = False
        
    def getName(self):
        return self.data['name']

    def getType(self):
        return self.data['type'].lower()

    def getAttr(self, attrName):
        if attrName.lower() in self.data.keys():
            return self.data[attrName.lower()].lower()
        raise KeyError

    def setAttr(self, attrName, attrValue):
        if attrName.lower() in self.data.keys():
            self.data[attrName.lower()] = attrValue
        else:
            raise KeyError

    def getJson(self):
        return self.data


def createCharacter(name, strType, ownerName):
    hero = Character(name, strType, ownerName)
    return hero
