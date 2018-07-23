'''
    Gloomhaven Characters have the following attributes:

        # DONE
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

        # DONE
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
from effects import *

class Character():
    _valid_actions = ['play_cards', 'long_rest']

    def __init__(self, name, type, owner='<UNKNOWN>', level=1, xp=0, gold=30, quest=0, checkmarks=0):
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

        self.effects = initEffects()

    def selectAction(self):
        self.round_action = pickRandom(_valid_actions)

    def endTurn(self):
        # remove one-round long effects
        for eff in _one_turn_effects:
            self.effects[eff.lower()] = False

    def isExhausted(self):
        return self.data['exhausted']

    def heal(self, value):
        if self.underEffect('Wound'):
            setEffect(self.effects, 'Wound', False)
            # do no return as heal continues

        if self.underEffect('Poison'):
            setEffect(self.effects, 'Poison', False)
            # if curing poison heal has no other effect
            # if wounded & poisoned both are removed but
            # no health is gain, hence the order
            return

        self.data['curr_health'] = min(self.data['max_health'], self.data['curr_health']+value)

    # take damage assumes the decison to take damage was made by the player
    # in lieu of remove cards from their hand or discard pile
    # Also, additional damage from any Effects should be included
    def takeDamage(self, amount, effList=[]):
        assert (self.data['curr_health'] - amount) >= 1
        try:
            self.data['curr_health'] = self.data['curr_health'] - amount
        except AssertionError as err:
            print('[takeDamage :: AssertionError] : %s' % err)
            raise

    def numPotionsAllowed(self):
        return int(0.5 + self.getLevel() / 2.)

    def getName(self):
        return self.data['name']

    def getType(self):
        return self.data['type'].lower()

    def getLevel(self):
        return self.data['level']

    def getAttr(self, attrName):
        if attrName.lower() in self.data.keys():
            return self.data[attrName.lower()].lower()
        raise KeyError

    def underEffect(self, effectName):
        return self.effects[effectName.lower()]

    def setAttr(self, attrName, attrValue):
        if attrName.lower() in self.data.keys():
            self.data[attrName.lower()] = attrValue
        else:
            raise KeyError

    def getJson(self):
        return self.data


def createCharacter(name, strType, ownerName, level=1):
    hero = Character(name, strType, ownerName, level=level)
    return hero
