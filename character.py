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

valid_types = ['Brute', 'Cragheart', 'Tinkerer', 'Scoundrel', 'Spellweaver', 'Mindthief']

class Character():
    def __init__(self, name, type, owner='<UNKNOWN>'):
        assert type in valid_types
        
        self.data = {}
        self.data['Name'] = name
        self.data['Type'] = type
        self.data['Owner'] = owner
        
    def getName(self):
        return self.data['Name']

    def getType(self):
        return self.data['Type']

    def getJson(self):
        return self.data


def createCharacter(name, type, ownerName):
    hero = Character(name, type, ownerName)
    return hero