'''
    Base Class for all player and non-player characters
    Inherited by npc.py (for enemies and spawns)
    Inherited by character.py (for heroes)
'''

from effects import *
from ability_cards import HeroAbilityCardDeck, MonsterAbilityCardDeck

class Unit():
    def __init__(self, name, max_hp=0):
        self.name           = name
        self.max_hp         = max_hp
        self.curr_hp        = max_hp
        self.ability_deck   = None
        self.effects        = initEffects()

        self.location       = None

    def setLocation(self, row, col):
        self.location = Location(row, col)

    def getLocation(self):
        return self.location

    def setHealth(self, value):
        self.max_hp = value
        self.curr_hp = value

    def setAbilityCardDeck(self, deck):
        assert isinstance(deck, HeroAbilityCardDeck) or isinstance(deck, MonsterAbilityCardDeck)
        self.ability_deck = deck

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
        self.curr_hp = min(self.max_hp, self.curr_hp+value)

    def takeDamage(self, amount, effList=[]):
        raise Exception("[BASE UNIT CLASS] :: Implement in parent")

    def selectAction(self):
        raise Exception("[BASE UNIT CLASS] :: Implement in parent")

    def endTurn(self):
        # remove one-round long effects
        removeOneTurnEffects(self.effects)

    def underEffect(self, effectName):
        return self.effects[effectName.lower()]

    def getName(self):
        return self.name

    def __repr__(self):
        str  = "[%s]" % (self.name)
        return str

if __name__ == "__main__":
    un = Unit("Skeleton Archer")
    print(un)
