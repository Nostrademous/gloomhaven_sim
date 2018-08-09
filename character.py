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
from utils import *
from effects import *
from unit import Unit
from ability_cards import HeroAbilityCardDeck

import perks
import amd

class Character(Unit):
    _valid_actions = ['play_cards', 'long_rest']

    def __init__(self, name, type, owner='<UNKNOWN>', level=1, xp=0, gold=30, quest=0, checkmarks=0):
        print('Name: %s' % name)
        super().__init__(name, 0)
        self.type           = type
        self.owner          = owner
        self.level          = level
        self.xp             = xp
        self.gold           = gold
        self.quest          = quest # for tracking retirement conditions
        self.checkmarks     = checkmarks
        self.perks_from_chk = 0
        self.available_perks= perks.getPerkSelections(self.type)
        self.selected_perks = list()

        if gv.heroDataJson:
            self.curr_hp    = int(gv.heroDataJson[type.capitalize()]['Health'][str(level)])
            self.max_hp     = int(self.curr_hp)
            self.deck_size  = int(gv.heroDataJson[type.capitalize()]['DeckSize'])

        self.retired        = False
        self.exhausted      = False

        self.effects        = initEffects()
        self.items          = list()
        self.amd            = amd.AttackModifierDeck(isPlayer=True)
        self.long_rest      = False
        self.round_init     = 99

    def scenarioPreparation(self):
        self.setAbilityCardDeck(HeroAbilityCardDeck(self.type, self.level))
        self.ability_deck.selectCardsFromFullDeck(self.deck_size)

        # adjust attack modifier deck for perks
        self.adjustAMD()

    def adjustAMD(self):
        """ Adjustment are sometimes required for the following:
            * Items (some items add -1 cards and others)
            * Perks
            * Scenario Specific (some add curses, etc)
        """
        print("[%s][adjustAMD] for perks... - IMPLEMENT" % (self.getName()))

    def selectAction(self):
        if self.isExhausted(): return

        if self.ability_deck.getNumRemainingCards() < 2:
            self.round_action = "long_rest"
        else:
            self.round_action = pickRandom(self._valid_actions)

        if self.round_action == 'play_cards':
            topCard = self.ability_deck.selectRoundCards()
            play_cards = self.ability_deck.in_hand_cards
            self.round_init = play_cards[topCard].getInitiative()
            print("[%s] Initiative: %d" % (self.getName(), self.round_init))
            if topCard == 0:
                print(play_cards[0])
                print(play_cards[1])
            else:
                print(play_cards[1])
                print(play_cards[0])
        else:
            print("[%s] Taking Long Rest" % (self.getName()))
            self.long_rest = True
            self.round_init = 99

    def endTurn(self):
        # call base class to remove one-round effects
        super().endTurn()

        if self.long_rest:
            self.heal(2)
            self.long_rest = False
            if self.ability_deck:
                lossCard = self.ability_deck.pickRandomDiscardedCardForLoss()
                self.ability_deck.recoverDiscardedCards(lossCard)

    def isExhausted(self):
        return self.exhausted

    def getPerkCount(self):
        return self.perks_from_chk + self.level - 1

    def addCheckmark(self, cnt=1):
        self.checkmarks += cnt
        if self.checkmarks >= 3:
            extra_perks = int(self.checkmarks/3)
            # max extra perks from checkmarks is 6 per char sheet
            if self.perks_from_chk < 6:
                # I believe below is safe as I don't see a way to
                # get more than 3 checkmarks in a single scenario
                self.perks_from_chk += extra_perks
                self.addPerk(extra_perks)
                self.checkmarks = self.checkmarks % 3

    def loseCheckmark(self, cnt=1):
        self.checkmarks = max(0, self.checkmarks-cnt)

    def addPerk(self, perk=None):
        if not perk:
            perk = pickRandom(self.available_perks)
        print('Perk Selected: %s' % (perk))
        try:
            self.available_perks.remove(perk)
            self.selected_perks.append(perk)
        except Exception as err:
            print(err)
            raise err

    # take damage assumes the decison to take damage was made by the player
    # in lieu of remove cards from their hand or discard pile
    # Also, additional damage from any Effects should be included
    def takeDamage(self, amount, effList=[]):
        assert (self.curr_hp - amount) >= 1
        try:
            self.curr_hp = self.curr_hp - amount
        except AssertionError as err:
            print('[takeDamage :: AssertionError] : %s' % err)
            raise

    def numPotionsAllowed(self):
        return int(0.5 + self.getLevel() / 2.)

    def canLevel(self):
        if self.level == 9:
            return False

        inc = [45 + (5*(i-1)) for i in range(1,9)]
        if self.xp >= sum(inc[:self.level]):
            return True
        return False

    def getName(self):
        return self.name

    def getType(self):
        return self.type.lower()

    def getLevel(self):
        return self.level

    def addItem(self, itemName):
        self.items.append(itemName)

    def getJson(self):
        jsonData = {}
        jsonData['name'] = self.name
        jsonData['type'] = self.type
        jsonData['owner'] = self.owner
        jsonData['level'] = self.level
        jsonData['xp'] = self.xp
        jsonData['gold'] = self.gold
        jsonData['quest'] = self.quest
        jsonData['checkmarks'] = self.checkmarks

        if gv.heroDataJson:
            jsonData['curr_hp'] = self.curr_hp
            jsonData['max_hp'] = self.max_hp
            jsonData['deck_size'] = self.deck_size

        jsonData['retired'] = self.retired
        jsonData['items'] = self.items
        jsonData['perks'] = [str(p) for p in self.selected_perks]
        return jsonData

