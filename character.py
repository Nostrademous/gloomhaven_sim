'''
    Gloomhaven Characters have the following attributes:
        # Stage 3 implementation tracking
        Spawns: list(class units.py)

        # Stage 4 implementation tracking
        Items: list(class items.py)
'''

import copy
import json
import itertools
import global_vars as gv
from utils import *
from effects import *
from unit import Unit
from ability_cards import HeroAbilityCardDeck, DEFAULT, interpretCardSection

import perks
import amd
import items

_item_template = {
    "HEAD": None,
    "BODY": None,
    "HANDS": list(),
    "LEGS": None,
    "SMALL_ITEM": list()
}

class CharacterItem():
    def __init__(self):
        self.equipped_items = copy.deepcopy(_item_template)
        self.unequipped_items = list()

    def equipItem(self, itemObj, maxSmallItems=1):
        if itemObj.slot == "TWO_HANDS":
            assert len(self.equipped_items["HANDS"]) == 0
            self.equipped_items["HANDS"].append(itemObj)
        elif itemObj.slot == "ONE_HAND":
            assert len(self.equipped_items["HANDS"]) < 2
            self.equipped_items["HANDS"].append(itemObj)
        elif itemObj.slot == "SMALL_ITEM":
            assert len(self.equipped_items[itemObj.slot]) < maxSmallItems
            self.equipped_items["SMALL_ITEM"].append(itemObj)
        else:
            assert self.equipped_items[itemObj.slot] == None
            self.equipped_items[itemObj.slot] = itemObj

    def unequipItem(self, slot):
        if slot in ["HANDS", "SMALL_ITEM"]:
            assert len(self.equipped_items[slot]) > 0
        else:
            assert self.equipped_items[slot] != None
        self.unequipped_items.append(self.equipped_items[slot])
        self.equipped_items[slot] = None

    def sellItem(self, itemName):
        for item in self.unequipped_items:
            if item.name == itemName:
                self.unequipped_items.remove(item)
                return item.sellCost()
        # if we get here the item wasn't in our unequipped list
        for item in self.equipped_items:
            if self.equipped_items[item].name == itemName:
                cost = self.equipped_items[item].sellCost()
                self.equipped_items[item] = None
                return cost
        raise Exception("CharacterItem::sellItem", "'%s' not found" % (itemName))
        return 0

    def __repr__(self):
        ret = ""
        for item in self.equipped_items:
            ret += "%s\n" % (self.equipped_items[item])
        return ret

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getJSON(self):
        ret  = dict()
        for slot in _item_template:
            if self.equipped_items[slot] == None or self.equipped_items[slot] == []:
                ret[slot] = 'None'
            else:
                #ret += '%s: %s,' % (slot, self.equipped_items[slot].name)
                if isinstance(self.equipped_items[slot], list):
                    ret[slot] = [i.name for i in self.equipped_items[slot]]
                else:
                    ret[slot] = self.equipped_items[slot].name
        return ret


class Owner():
    def __init__(self, name):
        self.name       = name
        self.hero       = None
        self.retiredCnt = 0

        self.retiredHeroes = list()

    '''
    def setHero(self, heroObj):
        assert self.hero == None
        self.hero       = heroObj

    def getHero(self):
        return self.hero
    '''

    def retireHero(self, heroObj):
        self.retiredCnt += 1
        self.hero       = None
        self.retiredHeroes.append(copy.deepcopy(heroObj))

    def getRetiredCount(self):
        return self.retiredCnt

    def __repr__(self):
        retStr  = "Owner: %s\n" % (self.name)
        return retStr

    def getJson(self):
        retDict = {}
        retDict['Name'] = self.name
        retDict['RetiredHeroes'] = self.retiredCnt
        return retDict


class Character(Unit):
    _valid_actions = ['play_cards', 'long_rest']

    def __init__(self, name, heroType, ownerObj, level=1, xp=0, gold=30, quest=0, checkmarks=0):
        #print('Name: %s' % name)
        super().__init__(name, 0)
        self.type           = heroType
        self.owner          = ownerObj
        self.level          = level
        self.xp             = xp
        self.gold           = gold
        self.quest          = quest # for tracking retirement conditions
        self.checkmarks     = checkmarks
        self.perks_from_chk = 0
        self.available_perks= copy.deepcopy(perks.getPerkSelections(self.type))
        self.selected_perks = list()

        if gv.heroDataJson:
            self.curr_hp    = int(gv.heroDataJson[self.type.capitalize()]['Health'][str(level)])
            self.max_hp     = int(self.curr_hp)
            self.deck_size  = int(gv.heroDataJson[self.type.capitalize()]['DeckSize'])

        self.retired        = False
        self.exhausted      = False

        self.effects        = initEffects()
        self.temp_items     = list()
        self.items          = CharacterItem()
        self.amd            = amd.AttackModifierDeck(isPlayer=True)
        self.long_rest      = False
        self.round_init     = 99

        self.default_action = DEFAULT

    def scenarioPreparation(self, negativeEffects=list()):
        self.setAbilityCardDeck(HeroAbilityCardDeck(self.type, self.level))
        self.ability_deck.selectCardsFromFullDeck(self.deck_size)

        # adjust attack modifier deck for perks
        self.adjustAMD(negativeEffects)

    def adjustAMD(self, negativeEffects):
        """ Adjustment are sometimes required for the following:
            * Items (some items add -1 cards and others)
            * Perks
            * Scenario Specific (some add curses, etc)
        """
        print("[%s][adjustAMD] for perks... - IMPLEMENT" % (self.getName()))

        if len(negativeEffects) > 0 and not self.hasNegativeScenarioEffectImmunity():
            print("[%s][adjustAMD for Negative Scenario Effects] - IMPLEMENT ME")

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

            self.default_action.setInitiative(self.round_init)
        else:
            print("[%s] Taking Long Rest" % (self.getName()))
            self.long_rest = True
            self.round_init = 99

    def retire(self):
        self.retired = True
            
    def getRoundAbilityCards(self):
        return self.ability_deck.in_hand_cards

    def getRoundAbilitySelection(self):
        tops = list([DEFAULT.getTop()])
        bots = list([DEFAULT.getBottom()])
        for card in self.getRoundAbilityCards():
            tops.append(card.getTop())
            bots.append(card.getBottom())
        return tops, bots

    def getRoundInitiative(self):
        return self.round_init

    def executeTurn(self):
        print("[character::executeTurn] - IMPLEMENT ME")

        # if we are not long resting
        if not self.long_rest:
            top_actions, bot_actions = self.getRoundAbilitySelection()

            available_actions = itertools.product(top_actions, bot_actions)
            ordered_action = { "0": None, "1": None }
            for i,action in enumerate(available_actions):
                print("%d - %s" % (i, str(action)))
                topActionDict = interpretCardSection(action[0])
                botActionDict = interpretCardSection(action[1])

            # TODO - remove this
            ordered_action["0"] = pickRandom(top_actions)
            ordered_action["1"] = pickRandom(bot_actions)
            print("\n\nCHOSEN:\n\n", ordered_action)

            assert ordered_action["0"] and ordered_action["1"]
            assert len(ordered_action) == 2

            for i,action in enumerate(ordered_action):
                print("\n\n")
                print(ordered_action[action])
                print("\n\n")
                action = interpretCardSection(ordered_action[action])
                for actionIndx in action:
                    specific_action = action[actionIndx]
                    if specific_action.type == 'Move':
                        maxMoveDist = specific_action.data['MoveValue']
                        locTarget = gv.Location(0,0) # TODO - pick location
                        self.doMove(locTarget)
                    elif specific_action.type == 'Attack':
                        print("Whee I melee attack!!!")
                    elif specific_action.type == 'RangedAttack':
                        print("Whee I range attack!!!")
                    elif specific_action.type == 'RangedHeal':
                        print("healbot from range")
            exit(0)

    def endTurn(self):
        # call base class to remove one-round effects
        super().endTurn()

        # reset our play-cards to nothing
        self.play_cards = None
        self.default_action.setInitiative(100) # just incase

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

    def hasNegativeScenarioEffectImmunity(self):
        if perks.ignore_scen_perk in self.selected_perks: return True
        if perks.ignore_scen_perk_plus_1 in self.selected_perks: return True
        return False

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
            print('Perk Randomed: %s' % (perk))
        else:
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

    def numSmallItemsAllowed(self):
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

    def buyItem(self, itemName, adjustGold=True):
        item = items.createItem(itemName)
        if item:
            try:
                if adjustGold:
                    assert self.gold >= item.cost
                    self.gold -= item.cost
                self.items.equipItem(item, self.numSmallItemsAllowed())
            except AssertionError:
                print("You do not have enough gold to buy %s" % (itemName))

    def findItem(self, itemName):
        self.buyItem(itemName, adjustGold=False)

    def sellItem(self, itemName):
        gold_value = self.items.sellItem(itemName)
        self.gold += gold_value

    # TEMPORARY PLACEHOLDER FOR TRACKING CAMPAIGN PROGRESS
    def addItem(self, itemName):
        self.temp_items.append(itemName)

    def getJson(self):
        jsonData = {}
        jsonData['name'] = self.name
        jsonData['type'] = self.type
        jsonData['owner'] = self.owner.getJson()
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
        jsonData['items'] = self.items.getJSON()
        jsonData['item_strings'] = self.temp_items
        jsonData['perks'] = [str(p) for p in self.selected_perks]
        return jsonData

