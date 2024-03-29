'''
    A Gloomhaven Party has the following attributes:
        # Stage 1 implementation
        Name: (name of party)
        Members: (list class characters.py)
        ValidHeroTypes: (list string literals)

        # Stage 2 implementation
        Prosperity: (float literal - default 1.0)

        # Stage 3 implementation
        ScenariosCompleted: (list integer literals)
        ScenariosAvailable: (list integer literals)

        # Stage 4 implementation
        GlobalAchievements: list(strings)
        PartyAchievements: list(stings)

        # Stage 5 implementation
        TreasuresLooted: list(integer literals)
        CityQuestsDone: list(integer literals)
        RoadQuestsDone: list(integer literals)
'''

import math
import json
import character as ch
from utils import printJson, pickRandom
from perks import *
from items import findItemByID, findItemByName
from global_vars import *

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.owners     = list()
        self.members    = list()
        self.valid_hero_types   = list(starting_hero_types)
        self.retired_heroes     = list()
        self.party_json['Reputation'] = 0
        self.party_json['UnlockedCityEvents'] = list()
        self.party_json['CompletedCityEvents'] = list()
        self.party_json['UnlockedRoadEvents'] = list()
        self.party_json['CompletedRoadEvents'] = list()
        self.party_json['UnlockedRiftEvents'] = list()
        self.party_json['CompletedRiftEvents'] = list()
        self.party_json['ActiveQuests'] = list()
        self.party_json['CompletedQuests'] = list()
        self.party_json['ScenariosCompleted'] = list()
        self.party_json['ScenariosBlocked'] = list()
        self.party_json['ScenariosAvailable'] = list()
        self.party_json['TreasuresLooted'] = list()
        self.party_json['GlobalAchievements'] = list()
        self.party_json['PartyAchievements'] = list()
        self.party_json['AncientTechnology'] = 0
        self.party_json['GloomhavenProsperity'] = { 'Level': 1, 'Checkmarks': 0, 'Count': 0 }
        self.party_json['SanctuaryDonations'] = 0
        self.party_json['PartyEnhancements'] = dict()
        self.party_json['GloomhavenStore'] = getItemsAtProsperityLevel(1)

    def addEnhancement(self, strHeroName, intAbilityId, section, enhancement, gold=0):
        heroIndex = self.getHeroIndexByName(strHeroName)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            strHeroType = heroObj.getType().lower()

            if strHeroType not in self.party_json['PartyEnhancements']:
                self.party_json['PartyEnhancements'][strHeroType] = dict()

            if str(intAbilityId) not in self.party_json['PartyEnhancements'][strHeroType]:
                self.party_json['PartyEnhancements'][strHeroType][str(intAbilityId)] = dict()
                self.party_json['PartyEnhancements'][strHeroType][str(intAbilityId)]["Top"] = list()
                self.party_json['PartyEnhancements'][strHeroType][str(intAbilityId)]["Bottom"] = list()

            if section in ["Top", "Bottom"]:
                self.party_json['PartyEnhancements'][strHeroType][str(intAbilityId)][section].append(enhancement)
            else:
                raise Exception("[party - addEnhancement]", "Invalid Section: '%s' :: %s %s" % (section, strHeroType, str(intAbilityId)))

            if gold > 0:
                assert heroObj.gold >= gold
                heroObj.gold -= gold
                print("%s Bought Enhancement :: gold remaining: %d" % (strHeroName, heroObj.gold))

            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
        else:
            raise Exception("[party - addEnhancement]", "Failed to find hero: '%s'" % (strHeroName))

    def getNumEnhancementForHeroType(self, strHeroType):
        if strHeroType.lower() not in self.party_json['PartyEnhancements']:
            return 0
        count = 0
        for key in self.party_json['PartyEnhancements'][strHeroType.lower()]:
            count += len(self.party_json['PartyEnhancements'][strHeroType.lower()]["Top"])
            count += len(self.party_json['PartyEnhancements'][strHeroType.lower()]["Bottom"])
        return count

    def adjustReputation(self, amount):
        old = self.party_json['Reputation']
        new = min(max(old + amount, -20), 20)
        self.party_json['Reputation'] = new
        print("Party Reputation Changed from %d --> %d" % (old, new))
        if calculateShopModifier(new) != 0:
            print("New Shop Cost Modifier: %d" % (calculateShopModifier(new)))

    def makeSanctuaryDonation(self, strHeroName=None):
        self.party_json['SanctuaryDonations'] += 1
        if strHeroName:
            print("%s Donates to the Sanctuary of the Greak Oak - bless you!!!" % (strHeroName))
            self.heroAdjustGold(strHeroName, -10)

        # code to add prosperity checkmarks from donations
        cnt = self.party_json['SanctuaryDonations']
        if cnt > 9 and (cnt % 5) == 0:
            self.addProsperityCheckmark('Sanctuary Donation #%d' % (cnt))

    def calcAvgLevel(self):
        sumLevel = 0
        cnt      = 0
        for hero in self.members:
            if not hero.retired:
                #print(hero, hero.getLevel())
                sumLevel += hero.getLevel()
                cnt += 1
        avgLevel = sumLevel / cnt
        return math.ceil(avgLevel/2.0)

    def addActiveQuest(self, value):
        assert value not in self.party_json['ActiveQuests']
        assert value not in self.party_json['CompletedQuests']
        self.party_json['ActiveQuests'].append(value)

    def completeQuest(self, value):
        assert value in self.party_json['ActiveQuests']
        self.party_json['ActiveQuests'].remove(value)
        self.party_json['CompletedQuests'].append(value)

    def addGlobalAchievement(self, text):
        print("\nGlobal Achievement: '%s' obtained!!!" % (text))
        if text.upper() == 'ANCIENT TECHNOLOGY':
            self.party_json['AncientTechnology'] += 1
            if self.party_json['AncientTechnology'] >= 5:
                print("\n\nOpen Envelope A!!!!!\n\n")
            else:
                print("\n%d more needed before Envelope event\n" % (5-self.party_json['AncientTechnology']))
        self.party_json['GlobalAchievements'].append(text)

    def addPartyAchievement(self, text):
        self.party_json['PartyAchievements'].append(text)
        print("\nParty Achievement: '%s' obtained!!!" % (text))

    def addScenarioCompleted(self, value):
        self.party_json['ScenariosCompleted'].append(value)
        print("\nScenario #%d Completed!" % (value))
        if value in self.party_json['ScenariosAvailable']:
            self.party_json['ScenariosAvailable'].remove(value)

    def addScenarioAvailable(self, value):
        if value not in self.party_json['ScenariosCompleted'] and \
           value not in self.party_json['ScenariosBlocked']:
            self.party_json['ScenariosAvailable'].append(value)
            print("New Scenario Available: %d" % (value))

    def addScenarioBlocked(self, value):
        self.party_json['ScenariosBlocked'].append(value)
        if value in self.party_json['ScenariosAvailable']:
            self.party_json['ScenariosAvailable'].remove(value)
        print("Scenario Blocked: %d" % (value))

    def addTreasureLooted(self, value, strHero=''):
        assert value not in self.party_json['TreasuresLooted']
        try:
            self.party_json['TreasuresLooted'].append(value)
            print("\n%s looted treasure #%d" % (strHero, value))
        except AssertionError as err:
            print("[addTreasureLooted :: AssertionError] %s" % (err))
            raise

    def completeRiftEvent(self, value):
        try:
            assert value not in self.party_json['CompletedRiftEvents']
            self.party_json['CompletedRiftEvents'].append(value)
            print("\nCompleted Rift Event: %d" % (value))
        except AssertionError as err:
            print('[completeRiftEvent:: AssertionError] %s' % (err))
            raise

    def completeRoadEvent(self, value):
        try:
            assert value not in self.party_json['CompletedRoadEvents']
            self.party_json['CompletedRoadEvents'].append(value)
            print("\nCompleted Road Event: %d" % (value))
        except AssertionError as err:
            print('[completeRoadEvent:: AssertionError] %s' % (err))
            raise

    def completeCityEvent(self, value):
        try:
            assert value not in self.party_json['CompletedCityEvents']
            self.party_json['CompletedCityEvents'].append(value)
            print("\nCompleted City Event: %d" % (value))
            if value in self.party_json['UnlockedCityEvents']:
                self.party_json['UnlockedCityEvents'].remove(value)
        except AssertionError as err:
            print('[completeCityEvent:: AssertionError] %s' % (err))
            raise

    def unlockCityEvent(self, value):
        try:
            assert value not in self.party_json['UnlockedCityEvents']
            self.party_json['UnlockedCityEvents'].append(value)
            print('Adding City Event: %d' % (value))
            if value in self.party_json['CompletedCityEvents']:
                self.party_json['CompletedCityEvents'].remove(value)
        except AssertionError as err:
            print('[unlockCityEvent :: AssertionError] %s :: value: %d' % (err, value))
            raise

    def unlockRiftEvent(self, value):
        try:
            assert value not in self.party_json['UnlockedRiftEvents']
            self.party_json['UnlockedRiftEvents'].append(value)
        except AssertionError as err:
            print('[unlockRiftEvent :: AssertionError] %s' % (err))
            raise

    def unlockRoadEvent(self, value):
        try:
            assert value not in self.party_json['UnlockedRoadEvents']
            self.party_json['UnlockedRoadEvents'].append(value)
        except AssertionError as err:
            print('[unlockRoadEvent :: AssertionError] %s' % (err))
            raise

    def drawRandomCityEvent(self, maxID=30):
        pool = [i for i in range(1,maxID+1)] # +1 to make it inclusive
        for unlocked in self.party_json['UnlockedCityEvents']:
            #print("Removing City Event: %s" % str(unlocked))
            pool.append(unlocked)
        for done in self.party_json['CompletedCityEvents']:
            #print("Removing City Event: %s" % str(done))
            if done in pool:
                pool.remove(done)
        self.party_json['UnlockedCityEvents'] = pool
        print("City Events Available: %s" % self.party_json['UnlockedCityEvents'])
        if len(pool) > 0:
            drawn = pickRandom(pool)
            return drawn
        else:
            print("No More City Events Available")
            return 999

    def drawRandomRiftEvent(self, maxID=0):
        pool = [] #[i for i in range(1,maxID+1)] # +1 to make it inclusive
        for unlocked in self.party_json['UnlockedRiftEvents']:
            pool.append(unlocked)
        for done in self.party_json['CompletedRiftEvents']:
            if done != 999:
                pool.remove(done)
        self.party_json['UnlockedRiftEvents'] = pool
        print("Rift Events Available: %s" % self.party_json['UnlockedRiftEvents'])
        if len(pool) > 0:
            drawn = pickRandom(pool)
            return drawn
        else:
            print("No More Rift Events Available!!!")
            return 999

    def drawRandomRoadEvent(self, maxID=30):
        pool = [i for i in range(1,maxID+1)] # +1 to make it inclusive
        for unlocked in self.party_json['UnlockedRoadEvents']:
            pool.append(unlocked)
        for done in self.party_json['CompletedRoadEvents']:
            if done != 999:
                pool.remove(done)
        self.party_json['UnlockedRoadEvents'] = pool
        print("Road Events Available: %s" % self.party_json['UnlockedRoadEvents'])
        if len(pool) > 0:
            drawn = pickRandom(pool)
            return drawn
        else:
            print("No More Road Events Available!!!")
            return 999

    def drawRandomScenario(self):
        print("Scenarios Available to Play: %s\n" % self.party_json['ScenariosAvailable'])
        drawn = pickRandom(self.party_json['ScenariosAvailable'])
        return drawn

    def unlockHero(self, strHeroType):
        strHeroType = strHeroType.lower()
        # make hero available to pick (again)
        assert strHeroType not in self.valid_hero_types
        self.valid_hero_types.append(strHeroType)
        print("\n\nNEW CLASS UNLOCKED: %s\n\n" % (strHeroType.upper()))

    def retireHero(self, heroObj):
        for member in self.members:
            if heroObj.getName() is member.getName():
                print("\n<><> Retiring '%s'!!!\n" % member.getName())
                # return all items to Gloomhaven store
                unequip_sell_list = [entry.name for entry in heroObj.items.unequipped_items]
                for item in unequip_sell_list:
                    print('Selling Unequipped Item: ', item)
                    self.heroSellItem(heroObj.getName(), item)
                for slot in heroObj.items.equipped_items:
                    print('Selling Equipped Item Slot: ', slot)
                    if isinstance(heroObj.items.equipped_items[slot], list):
                        if len(heroObj.items.equipped_items[slot]) > 0:
                            sell_list = [entry.name for entry in heroObj.items.equipped_items[slot]]
                            for entry in sell_list:
                                self.heroSellItem(heroObj.getName(), entry)
                    else:
                        item = heroObj.items.equipped_items[slot]
                        if item:
                            self.heroSellItem(heroObj.getName(), item.name)
                # mark personal quest as completed
                self.completeQuest(heroObj.quest)
                self.addProsperityCheckmark('%s retirement' % heroObj.getName())
                member.retire()
                self.party_json['Members'][heroObj.getName()] = member.getJson()
                break
        self.retireHeroType(heroObj.getType())

    def claimHeroType(self, heroType):
        heroType = heroType.lower()
        assert heroType in self.valid_hero_types
        self.valid_hero_types.remove(heroType)

    def retireHeroType(self, heroType):
        # make hero available to pick again
        assert heroType not in self.valid_hero_types
        self.valid_hero_types.append(heroType)

    def addPlayers(self, ownerList):
        for owner in ownerList:
            assert owner not in self.owners
            self.owners.append(owner)

    def addMember(self, heroObj):
        try:
            assert heroObj.getType() in self.valid_hero_types

            self.members.append(heroObj)
            self.party_json['Members'] = {}
            for k,v in enumerate(self.members):
                self.party_json['Members'][v.getName()] = v.getJson()

            self.addActiveQuest(heroObj.quest)
            self.claimHeroType(heroObj.getType())
            print("Added '%s - %s' to the party!" % (heroObj.getName(), heroObj.getType()))
        except:
            print("[addMember - Assertion Failed]")
            print("\tAttempted adding '%s'" % (heroObj.getType()))
            print('\tValidTypes: %s' % str(self.valid_hero_types))
            print('\tActiveQuests: %s' % str(self.party_json['ActiveQuests']))
            print('\tCompletedQuests: %s' % str(self.party_json['CompletedQuests']))
            raise

    def addProsperityCheckmark(self, reason='', cnt=1):
        self.party_json['GloomhavenProsperity']['Count'] += cnt

        '''This is Version 1 counts
        count_per_increment = [5,6,7,8,9,10,12,15]
        '''
        # version 2 counts
        count_per_increment = [4,5,6,7,8,9,11,14]
        count_req = [sum(count_per_increment[:i]) for i in range(1,10)]
        curr_cnt = self.party_json['GloomhavenProsperity']['Count']
        for index, value in enumerate(count_req):
            if curr_cnt < value:
                break
        index += 1
        if reason != '':
            print("Gloomhaven gains Prosperity Checkmark #%d :: Reason: '%s'" % (curr_cnt, reason))
        else:
            print("Gloomhaven gains Prosperity Checkmark #%d" % (curr_cnt))
        if index > self.party_json['GloomhavenProsperity']['Level']:
            print("\nGLOOMHAVEN LEVELED UP TO %d!!!!\n" % (index))
            new_items = getItemsAtProsperityLevel(index)
            self.party_json['GloomhavenStore'].extend(new_items)
            print("Add Items to Store :: %s" % new_items)
            print("Need %d Prosperity for next Level" % (value - curr_cnt))
        else:
            print("Need %d Prosperity for next Level" % (value - curr_cnt))
        self.party_json['GloomhavenProsperity']['Level'] = index
        self.party_json['GloomhavenProsperity']['Checkmarks'] = curr_cnt - count_req[index-2]

    def heroAdjustCheckmarks(self, strHero, amount=1):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            print("%s gains %d checkmark(s)" % (strHero, amount))
            heroObj.adjCheckmarks(amount)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
        else:
            raise Exception('party::heroAdjustCheckmarks', 'Failed to Find Hero: "%s"' % (strHero))

    def heroAdjustXP(self, strHero, amount):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.xp += amount
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            print("%s gains %d XP" % (strHero, amount))
            bCanLevel, shortXP = heroObj.canLevel()
            if bCanLevel:
                print("\n<><> %s CAN LEVEL UP to %d\n" % (strHero, heroObj.level+1))
            else:
                print("%s needs %d more XP to Level\n" % (strHero, shortXP))
        else:
            raise Exception('party::heroAdjustXP', 'Failed to Find Hero: "%s"' % (strHero))

    def heroAdjustGold(self, strHero, amount):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.gold = max(heroObj.gold + amount, 0)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            print("%s gains %d Gold" % (strHero, amount))
        else:
            raise Exception('party::heroAdjustGold', 'Failed to Find Hero: "%s"' % (strHero))

    def heroFindItem(self, strHero, strItemName):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.buyItem(strItemName, adjustGold=False)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            print("%s buys item [%s] :: gold remaining: %d" % (strHero, strItemName, heroObj.gold))
        else:
            raise Exception('party::heroBuyItem', 'Failed to Find Hero: "%s"' % (strHero))

    def heroBuyItem(self, strHero, strItemName, adjGold=True):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.buyItem(strItemName, adjustGold=adjGold, rep=self.party_json['Reputation'])
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            itemObj, itemIndx = findItemByName(strItemName)
            assert itemObj
            self.adjustGloomhavenStore(itemObj, -1)
            print("%s buys item [%s] :: gold remaining: %d" % (strHero, strItemName, heroObj.gold))
        else:
            raise Exception('party::heroBuyItem', 'Failed to Find Hero: "%s"' % (strHero))

    def heroSellItem(self, strHero, strItemName, adjGold=True):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.sellItem(strItemName)
            itemObj, itemIndx = findItemByName(strItemName)
            assert itemObj
            self.adjustGloomhavenStore(itemObj, 1)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            print("%s sells item [%s] :: gold remaining: %d" % (strHero, strItemName, heroObj.gold))
        else:
            raise Exception('party::heroSellItem', 'Failed to Find Hero: "%s"' % (strHero))

    def heroAddPerk(self, strHero, perk, strPerkReason=' Checkmark'):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.addPerk(perk, strPerkReason)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
        else:
            raise Exception('party::heroAddPerk', 'Failed to Find Hero: "%s"' % (strHero))

    def heroLevelUp(self, strHero, perk, card=None):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.levelUp()
            print("<><> %s Levels Up to %d" % (strHero, heroObj.getLevel()))
            if card:
                print("%s new Ability Card Selection: '%s'" % (strHero, card))
                heroObj.addCardSelection(card)
            heroObj.addPerk(perk)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
        else:
            raise Exception('party::heroLevelUp', 'Failed to Find Hero: "%s"' % (strHero))

    def heroGainCheckmarkPerk(self, strHero, perk):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.addCheckmarkPerk(perk)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
        else:
            raise Exception('party::heroGainCheckmarkPerk', 'Failed to Find Hero: "%s"' % (strHero))

    def getHeroIndexByName(self, strName):
        for index, heroObj in enumerate(self.members):
            #print('Comparing: %s to %s' % (heroObj.getName(), strName))
            if heroObj.getName() == strName:
                return index
        return -1

    def addItemDesign(self, index):
        if not isinstance(index, str): index = str(index)
        assert isinstance(itemDataJson, dict)
        try:
            item = findItemByID(index)
            self.adjustGloomhavenStore(item, cnt=item['MaxCount'])
        except Exception as e:
            print("Failed to find item with index: %s" % (index))
            raise e

    def adjustGloomhavenStore(self, item, cnt=1):
        if cnt > 0:
            for i in range(0,cnt):
                print('Adding %s to store' % (item))
                self.party_json['GloomhavenStore'].append(item)
                #print(self.party_json['GloomhavenStore'])
                #raise Exception('Done', 'Done')
        else:
            print('Remove %s from store' % (item))
            self.party_json['GloomhavenStore'].remove(item)

    def getPartySize(self):
        return len(self.members)

    def getJson(self):
        return self.party_json

    def saveParty(self):
        with open('%s_party.json' % self.party_json['PartyName'], 'w') as outfile:
            json.dump(self.party_json, outfile, indent=4)

    def loadParty(self, name):
        self.__init__(name)

        with open('%s_party.json' % name) as infile:
            self.party_json = json.load(infile)

        if 'Members' in self.party_json.keys():
            for k,v in enumerate(self.party_json['Members']):
                heroData = self.party_json['Members'][v]
                self.members.append(ch.Character(heroData['name'], heroData['type'], heroData['owner']))

def make_a_party():
    import global_vars as gv
    gv.init() # call only once

    party = Party('TheBrotherhood')

    party.adjustReputation(1)
    party.adjustReputation(-2)
    party.adjustReputation(2)
    party.adjustReputation(-1)
    party.adjustReputation(-1)
    party.adjustReputation(2)

    party.addGlobalAchievement('City Rule: Militaristic')
    party.addGlobalAchievement('The Power of Enhancement')
    party.addGlobalAchievement('The Merchant Flees')
    party.addGlobalAchievement('The Rift Neutralized')

    party.addPartyAchievement('First Steps')
    party.addPartyAchievement("Jekserah's Plans")
    party.addPartyAchievement("Tremors")
    party.addPartyAchievement("A Demon's Errand")

    party.completeCityEvent(4)
    party.completeCityEvent(14)
    party.completeCityEvent(15)
    party.completeCityEvent(17)
    party.completeCityEvent(18)
    party.completeCityEvent(19)
    party.completeCityEvent(21)
    party.completeCityEvent(27)
    party.completeCityEvent(28)
    party.completeCityEvent(30)
    party.addItemDesign(105)

    party.unlockCityEvent(73)
    party.completeCityEvent(73)
    party.unlockCityEvent(78) # Scenario 21 complete

    party.completeRoadEvent(1)
    party.completeRoadEvent(4)
    party.completeRoadEvent(7)
    party.completeRoadEvent(9)
    party.completeRoadEvent(11)
    party.completeRoadEvent(16)
    party.completeRoadEvent(17)
    party.completeRoadEvent(23)
    party.completeRoadEvent(25)

    party.unlockRoadEvent(65) # from City Event 21

    party.addScenarioCompleted(1)
    party.addScenarioCompleted(2)
    party.addScenarioCompleted(3)
    party.addScenarioCompleted(4)
    party.addScenarioCompleted(5)
    party.addScenarioCompleted(8)
    party.addScenarioCompleted(10)
    party.addScenarioCompleted(13)
    party.addScenarioCompleted(14)
    party.addScenarioCompleted(20)
    party.addScenarioCompleted(21)

    party.addScenarioBlocked(9)

    party.addScenarioAvailable(6)
    party.addScenarioAvailable(7)
    party.addScenarioAvailable(16)
    party.addScenarioAvailable(18)
    party.addScenarioAvailable(19)
    party.addScenarioAvailable(22)
    party.addScenarioAvailable(28)
    party.addScenarioAvailable(63)
    party.addScenarioAvailable(66)
    party.addScenarioAvailable(68)
    party.addScenarioAvailable(76)
    party.addScenarioAvailable(84)

    party.addProsperityCheckmark()
    party.addProsperityCheckmark()
    party.addProsperityCheckmark()
    party.addProsperityCheckmark()
    party.addProsperityCheckmark('Scenario #20 reward') # from Scenario 20

    party.addTreasureLooted(4)
    party.addTreasureLooted(7)
    party.addTreasureLooted(10)

    party.addTreasureLooted(11) # ItemID:85 "Wand of Inferno"
    party.addItemDesign(85)

    party.addTreasureLooted(15) # ItemID:45 "Pendant of Dark Pacts"
    party.addItemDesign(45)

    party.addTreasureLooted(26)
    party.addTreasureLooted(28) # +15 Gold - Kyle
    party.addTreasureLooted(38)
    party.addTreasureLooted(46)
    party.addTreasureLooted(51)
    party.addTreasureLooted(60) # ItemID: 113 "Skullbane Axe" - Danny
    party.addTreasureLooted(65)
    party.addTreasureLooted(67)

    party.addItemDesign(107) # Horned Helm

    owner_ag = ch.Owner('Andrzej')
    owner_dp = ch.Owner('Danny')
    owner_et = ch.Owner('Evan')
    owner_mc = ch.Owner('Matt')
    owner_ks = ch.Owner('Kyle')
    owner_michael = ch.Owner('Michael')
    owner_sm = ch.Owner('Stu')

    hero1 = ch.Character('Clockwerk', 'Tinkerer', owner_ag, level=5, xp=225, gold=24, quest=528, checkmarks=10)
    #print("Number Enhancements for %s: %d" % (hero1.getName(), party.getNumEnhancementForHeroType(hero1.getType())))
    hero1.addCheckmarkPerk(ignore_scen_perk)
    hero1.addPerk(remove_2_minus_1)
    hero1.addCheckmarkPerk(add_1_plus_3)
    hero1.addPerk(remove_2_minus_1)
    hero1.addCheckmarkPerk(replace_minus_2_with_0)
    hero1.addPerk(add_1_plus_1_wound)
    party.addMember(hero1)
    party.addEnhancement('Clockwerk', 36, "Top", 'Wound on Attack') # 75 gold paid
    party.addEnhancement('Clockwerk', 41, "Top", '+1 Range') # 30 gold paid
    hero1.scenarioPreparation()

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', owner_dp, level=3, quest=512, gold=191, xp=161, checkmarks=5)
    hero2.buyItem('Boots of Striding', adjustGold=False)
    hero2.buyItem('Minor Healing Potion', adjustGold=False)
    hero2.buyItem('Leather Armor', adjustGold=False)
    hero2.buyItem('Iron Helmet', adjustGold=False)
    hero2.findItem('Skullbane Axe')
    hero2.addCheckmarkPerk(replace_minus_1_with_plus_1)
    hero2.addPerk(remove_2_minus_1)
    hero2.addPerk(add_1_plus_3)
    party.addMember(hero2)
    party.addEnhancement('Ruby Sweety Pie', 6, "Bottom", '+1 Move') # 30 gold paid

    hero3 = ch.Character('Evan', 'Spellweaver', owner_et, level=4, quest=533, gold=39, xp=208, checkmarks=9)
    hero3.addCheckmarkPerk(add_2_plus_1)
    hero3.addPerk(add_2_plus_1)
    hero3.addCheckmarkPerk(add_1_plus_1_wound)
    hero3.addPerk(add_1_plus_2_fire)
    hero3.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero3)
    party.heroBuyItem('Evan', 'Cloak of Invisibility', adjGold=False)
    party.heroBuyItem('Evan', 'Minor Power Potion', adjGold=False)
    party.heroBuyItem('Evan', 'Eagle-Eye Goggles', adjGold=False)
    party.heroBuyItem('Evan', 'Piercing Bow', adjGold=False)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', owner_mc, level=4, quest=531, gold=32, xp=203, checkmarks=8)
    hero4.addCheckmarkPerk(ignore_item_perk)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addCheckmarkPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(remove_4_0)
    party.addMember(hero4)
    party.heroBuyItem('Bloodfist Stoneborn', 'Hide Armor', adjGold=False)
    party.heroBuyItem('Bloodfist Stoneborn', 'Boots of Striding', adjGold=False)
    party.heroBuyItem('Bloodfist Stoneborn', 'Minor Stamina Potion', adjGold=False)
    party.heroBuyItem('Bloodfist Stoneborn', 'Horned Helm', adjGold=False)
    party.heroBuyItem('Bloodfist Stoneborn', 'Heater Shield', adjGold=False)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', owner_ks, level=4, quest=526, gold=40, xp=186, checkmarks=7)
    hero5.addCheckmarkPerk(ignore_scen_perk)
    hero5.addPerk(remove_2_minus_1)
    hero5.addCheckmarkPerk(replace_minus_2_with_0)
    hero5.addPerk(remove_2_minus_1)
    hero5.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero5)
    party.addEnhancement('Rabid Cicada', 102, "Bottom", 'Bless on Invisibility') # 100gold paid
    party.heroBuyItem('Rabid Cicada', 'Leather Armor', adjGold=False)
    party.heroBuyItem('Rabid Cicada', 'Poison Dagger', adjGold=False)
    party.heroBuyItem('Rabid Cicada', 'Winged Shoes', adjGold=False)
    party.heroBuyItem('Rabid Cicada', 'Minor Stamina Potion', adjGold=False)

    party.makeSanctuaryDonation() # Matt
    party.makeSanctuaryDonation() # scen 8 - (forgot)
    party.makeSanctuaryDonation() # scen 8 - Matt
    party.makeSanctuaryDonation() # scen 8 - Evan
    party.makeSanctuaryDonation() # scen 21 - Kyle
    party.makeSanctuaryDonation() # scen 21 - Andrzej
    party.makeSanctuaryDonation() # scen 21 - Danny
    party.makeSanctuaryDonation() # scen 13 - Kyle
    party.makeSanctuaryDonation() # scen 13 - Matt
    party.makeSanctuaryDonation() # scen 13 - Evan
    # 10 party donations ----- (also provided +1 prosperity)
    party.makeSanctuaryDonation() # scen 13 - Evan
    party.makeSanctuaryDonation() # scen 13 - Andrzej
    party.makeSanctuaryDonation() # scen 20 - Andrzej
    party.makeSanctuaryDonation() # scen 20 - Kyle

    party.heroFindItem('Rabid Cicada', 'Ring of Skulls')

    #########################################################################################
    # pre-play session Oct 1
    party.makeSanctuaryDonation('Clockwerk') # 15 (+1 prosperity) - Andrzej - pre-retirement

    party.retireHero(hero1)
    party.retireHero(hero2)
    party.unlockHero("Quartermaster")
    party.unlockHero("Doomstalker")

    hero6 = ch.Character('Singularity', 'Doomstalker', owner_ag, level=3, quest=530)
    hero6.addOwnerPerk(remove_2_minus_1)
    hero6.addPerk(remove_2_minus_1)
    hero6.addPerk(add_2_roll_plus_1)
    party.addMember(hero6)

    hero7 = ch.Character('Red', 'Quartermaster', owner_dp, level=3, quest=522)
    hero7.addOwnerPerk(ignore_item_perk_add_2_plus_1)
    hero7.addPerk(remove_2_minus_1)
    hero7.addPerk(remove_2_minus_1)
    party.addMember(hero7)

    party.unlockCityEvent(42) # Brute Retirement
    party.unlockRoadEvent(42) # Brute Retirement
    party.unlockCityEvent(43) # Tinkerer Retirement
    party.unlockRoadEvent(43) # Tinkerer Retirement
    party.unlockCityEvent(32) # Quartermaster Class Choice
    party.unlockRoadEvent(32) # Quartermaster Class Choice
    party.unlockCityEvent(38) # Doomstalker Class Choice
    party.unlockRoadEvent(38) # Doomstalker Class Choice

    # play session Oct 1
    party.heroBuyItem('Singularity', 'Boots of Striding')
    party.heroBuyItem('Singularity', 'Cloak of Invisibility')
    party.heroBuyItem('Singularity', 'Minor Power Potion')
    party.heroBuyItem('Singularity', 'Minor Stamina Potion')
    party.heroBuyItem('Red', 'Horned Helm')
    party.heroBuyItem('Red', 'War Hammer')
    party.heroSellItem('Bloodfist Stoneborn', 'Hide Armor')
    party.heroBuyItem('Bloodfist Stoneborn', 'Chainmail')
    party.heroSellItem('Rabid Cicada', 'Poison Dagger')
    print(party.party_json['GloomhavenStore'])
    party.heroBuyItem('Rabid Cicada', 'Skullbane Axe')

    party.completeCityEvent(20)
    party.heroAdjustGold('Bloodfist Stoneborn', 2)
    party.heroAdjustXP('Bloodfist Stoneborn', 5)
    party.heroAdjustGold('Rabid Cicada', 2)
    party.heroAdjustXP('Rabid Cicada', 5)
    party.heroAdjustGold('Evan', 2)
    party.heroAdjustXP('Evan', 5)
    party.heroAdjustGold('Singularity', 2)
    party.heroAdjustXP('Singularity', 5)
    party.heroAdjustGold('Red', 2)
    party.heroAdjustXP('Red', 5)

    party.heroLevelUp('Evan', add_1_plus_2_fire, "Chromatic Explosion")

    party.completeRoadEvent(19)
    party.adjustReputation(1) # from Road Event

    party.addTreasureLooted(17, 'Bloodfist Stoneborn') # Matt (+20 gold)
    party.heroAdjustGold('Bloodfist Stoneborn', 20)

    # adjustments for scenario completion (xp, gold, checkmarks)
    party.addScenarioCompleted(19)
    party.addPartyAchievement("Stonebreaker's Censer")
    party.addScenarioAvailable(27)
    party.addProsperityCheckmark('Scenario #19 reward') # For Scenario #19 completion
    party.heroAdjustGold('Bloodfist Stoneborn', 24)
    party.heroAdjustXP('Bloodfist Stoneborn', 20)
    party.heroAdjustCheckmarks('Bloodfist Stoneborn', 1)
    party.heroAdjustGold('Rabid Cicada', 18)
    party.heroAdjustXP('Rabid Cicada', 17)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustGold('Evan', 6)
    party.heroAdjustXP('Evan', 21)
    party.heroAdjustCheckmarks('Evan', 0)
    party.heroAdjustGold('Singularity', 9)
    party.heroAdjustXP('Singularity', 20)
    party.heroAdjustCheckmarks('Singularity', 0)
    party.heroAdjustGold('Red', 3)
    party.heroAdjustXP('Red', 20)
    party.heroAdjustCheckmarks('Red', 1)


    # Play Session - Oct 15
    party.heroGainCheckmarkPerk('Evan', add_1_plus_2_ice)
    party.heroLevelUp('Bloodfist Stoneborn', add_1_plus_2_muddle, "Stone Pummel")
    party.heroGainCheckmarkPerk('Bloodfist Stoneborn', add_1_plus_2_muddle)
    party.addEnhancement('Bloodfist Stoneborn', 127, "Top", '+1 on Push', gold=30) # 30gold paid
    party.makeSanctuaryDonation('Rabid Cicada') # 16
    party.makeSanctuaryDonation('Singularity') # 17

    party.completeCityEvent(11)
    party.addItemDesign(78) # Storm Blade
    party.heroAdjustGold('Rabid Cicada', -1)
    party.heroAdjustGold('Bloodfist Stoneborn', -1)
    party.heroAdjustGold('Evan', -1)
    party.heroAdjustGold('Singularity', -1)
    party.heroAdjustGold('Red', -1)
    party.completeRoadEvent(29)

    party.addTreasureLooted(50, 'Rabid Cicada')
    party.heroFindItem('Rabid Cicada', 'Second Skin')

    # adjustments for scenario completion (xp, gold, checkmarks)
    party.addScenarioCompleted(6)
    party.addPartyAchievement("Jekserah's Plans")
    party.addPartyAchievement("Dark Bounty")
    party.heroAdjustGold('Bloodfist Stoneborn', 8)
    party.heroAdjustXP('Bloodfist Stoneborn', 24)
    party.heroAdjustCheckmarks('Bloodfist Stoneborn', 1)
    party.heroAdjustGold('Rabid Cicada', 5)
    party.heroAdjustXP('Rabid Cicada', 11)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustGold('Evan', 20)
    party.heroAdjustXP('Evan', 12)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustGold('Singularity', 14)
    party.heroAdjustXP('Singularity', 22)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustGold('Red', 39)
    party.heroAdjustXP('Red', 20)
    party.heroAdjustCheckmarks('Red', 0)

    party.heroSellItem('Rabid Cicada', 'Second Skin')

    # Oct 22 Session
    party.heroLevelUp('Rabid Cicada', remove_4_0, "Visage of the Inevitable")
    party.heroGainCheckmarkPerk('Rabid Cicada', replace_0_with_plus_2)
    party.heroBuyItem('Rabid Cicada', 'Minor Mana Potion')
    party.heroBuyItem('Red', 'Hide Armor')
    party.heroBuyItem('Red', 'Winged Shoes')
    party.heroBuyItem('Red', 'Minor Stamina Potion')
    party.makeSanctuaryDonation('Rabid Cicada') # 18
    party.makeSanctuaryDonation('Singularity') # 19

    party.completeCityEvent(8)
    party.heroAdjustGold('Bloodfist Stoneborn', -4)
    party.heroAdjustGold('Rabid Cicada', -4)
    party.heroAdjustGold('Singularity', -4)
    party.heroAdjustGold('Red', -3)
    party.heroAdjustGold('Evan', -5)
    party.addPartyAchievement("A Map to Treasure")
    party.addScenarioAvailable(93)

    party.completeRoadEvent(8)

    party.addTreasureLooted(21, 'Red')
    party.addScenarioCompleted(22)
    party.addGlobalAchievement("Artifact Recovered")
    party.addScenarioAvailable(31)
    party.addScenarioAvailable(35)
    party.addScenarioAvailable(36)
    party.heroAdjustGold('Bloodfist Stoneborn', 15)
    party.heroAdjustXP('Bloodfist Stoneborn', 25)
    party.heroAdjustCheckmarks('Bloodfist Stoneborn', 1)
    party.heroAdjustGold('Rabid Cicada', 9)
    party.heroAdjustXP('Rabid Cicada', 22)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustGold('Evan', 6)
    party.heroAdjustXP('Evan', 25)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustGold('Singularity', 0)
    party.heroAdjustXP('Singularity', 26)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustGold('Red', 12)
    party.heroAdjustXP('Red', 22)
    party.heroAdjustCheckmarks('Red', 0)

    # Oct 29 Session
    party.heroLevelUp('Bloodfist Stoneborn', add_2_roll_earth, "Cataclysm")
    party.heroLevelUp('Singularity', add_2_roll_plus_1, "Flight of Flame")
    party.heroLevelUp('Red', add_2_roll_plus_1, "Scroll of Lightning")

    party.addEnhancement('Bloodfist Stoneborn', 119, "Bottom", '+1 on Move', gold=30) # 30gold paid
    party.heroBuyItem('Red', 'Minor Power Potion')

    party.completeCityEvent(16)
    party.heroAdjustGold('Bloodfist Stoneborn', -10)
    party.unlockCityEvent(70)

    party.makeSanctuaryDonation('Bloodfist Stoneborn') # 20
    party.makeSanctuaryDonation('Rabid Cicada') # 21

    party.completeRoadEvent(38)
    party.addProsperityCheckmark()

    party.addTreasureLooted(54, 'Red')
    party.heroFindItem('Red', 'Doomed Compass')

    party.addScenarioCompleted(93)
    party.heroAdjustGold('Bloodfist Stoneborn', 12)
    party.heroAdjustXP('Bloodfist Stoneborn', 33)
    party.heroAdjustCheckmarks('Bloodfist Stoneborn', 0)
    party.heroAdjustGold('Rabid Cicada', 12)
    party.heroAdjustXP('Rabid Cicada', 24)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustGold('Singularity', 12)
    party.heroAdjustXP('Singularity', 32)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustGold('Red', 18)
    party.heroAdjustXP('Red', 30)
    party.heroAdjustCheckmarks('Red', 1)

    # Back at Gloomhaven
    party.makeSanctuaryDonation('Bloodfist Stoneborn') # 21
    party.retireHero(hero4)
    party.addEnhancement('Bloodfist Stoneborn', 120, "Bottom", 'Strengthen', gold=50) # 50gold paid
    party.unlockCityEvent(46)
    party.unlockRoadEvent(46)
    party.unlockHero("Elementalist")
    party.unlockCityEvent(40)
    party.unlockRoadEvent(40)

    hero8 = ch.Character('Ignus', 'Elementalist', owner_mc, level=1, gold=60, xp=95, quest=524)
    hero8.addOwnerPerk([remove_2_0, add_1_0_fire, add_1_0_earth])
    party.addMember(hero8)
    party.heroLevelUp('Ignus', remove_2_minus_1, 'Crystallizing Blast')
    party.heroLevelUp('Ignus', remove_2_minus_1, 'Chain Lightning')
    party.heroBuyItem('Ignus', 'Chainmail')
    party.heroBuyItem('Ignus', 'Heater Shield')
    party.heroBuyItem('Ignus', 'Iron Helmet')
    party.heroBuyItem('Ignus', 'Minor Mana Potion')

    party.heroGainCheckmarkPerk('Singularity', replace_2_0_with_2_plus_1)

    party.completeCityEvent(10)
    party.heroAdjustGold('Singularity', -5)
    party.heroAdjustGold('Evan', -5)
    party.heroAdjustGold('Red', -5)
    party.heroAdjustGold('Rabid Cicada', -5)

    party.completeRoadEvent(27)

    party.addTreasureLooted(32, 'Rabid Cicada') # Item Design 76 - Chain Hood
    party.addItemDesign(76)

    party.addScenarioCompleted(28)
    party.addScenarioAvailable(29)
    party.addPartyAchievement('An Invitation')
    party.heroAdjustGold('Rabid Cicada', 12)
    party.heroAdjustXP('Rabid Cicada', 18)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustGold('Singularity', 18)
    party.heroAdjustXP('Singularity', 30)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustGold('Red', 12)
    party.heroAdjustXP('Red', 19)
    party.heroAdjustCheckmarks('Red', 0)
    party.heroAdjustGold('Evan', 9)
    party.heroAdjustXP('Evan', 19)
    party.heroAdjustCheckmarks('Evan', 1)

    party.heroAdjustXP('Rabid Cicada', 10)
    party.heroFindItem('Rabid Cicada', 'Silent Stiletto')
    party.heroLevelUp('Rabid Cicada', replace_0_with_plus_2, 'Burning Oil')
    party.heroLevelUp('Red', add_2_roll_plus_1, 'Reinforce Steel')
    party.heroLevelUp('Singularity', replace_2_0_with_2_plus_1, 'Wild Command')
    party.heroLevelUp('Evan', replace_minus_1_with_plus_1, 'Living Torch')
    party.heroGainCheckmarkPerk('Evan', [add_1_roll_light, add_1_roll_dark])
    party.heroBuyItem('Evan', 'Minor Stamina Potion')

    party.makeSanctuaryDonation('Rabid Cicada')

    party.completeCityEvent(6)
    party.heroAdjustXP('Rabid Cicada', 5)
    party.heroAdjustXP('Red', 5)
    party.heroAdjustXP('Singularity', 5)
    party.heroAdjustXP('Evan', 5)
    party.heroAdjustXP('Ignus', 5)
    party.addProsperityCheckmark('City Event 6')

    party.completeRoadEvent(28)
    party.heroAdjustGold('Red', 20)
    party.heroSellItem('Red', 'Minor Stamina Potion', adjGold=False)

    party.addScenarioCompleted(27)
    party.addGlobalAchievement('The Rift Neutralized')
    party.addProsperityCheckmark('Scenario 27 Completed')
    party.heroAdjustXP('Rabid Cicada', 17)
    party.heroAdjustXP('Red', 18)
    party.heroAdjustXP('Singularity', 19)
    party.heroAdjustXP('Evan', 19)
    party.heroAdjustXP('Ignus', 19)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Red', 1)
    party.heroAdjustCheckmarks('Singularity', 2)
    party.heroAdjustCheckmarks('Evan', 0)
    party.heroAdjustCheckmarks('Ignus', 1)
    
    party.heroSellItem('Rabid Cicada', 'Skullbane Axe')
    party.heroGainCheckmarkPerk('Singularity', replace_2_0_with_2_plus_1)
    party.heroGainCheckmarkPerk('Red', add_1_0_refresh_item)

    # scenario award - 100g to use for enhancements only
    party.addEnhancement('Singularity', 394, 'Top', '+1 Attack', gold=0) # 100gold paid
    party.addEnhancement('Ignus', 456, 'Top', '+1 Attack', gold=0) # 50gold paid
    party.addEnhancement('Ignus', 457, 'Bottom', '+1 Move', gold=0) # 50gold paid
    party.addEnhancement('Evan', 61, 'Top', '+1 Attack', gold=0) # 100gold paid
    party.addEnhancement('Rabid Cicada', 90, 'Bottom', '+1 Pull', gold=0) # 30gold paid
    party.addEnhancement('Rabid Cicada', 90, 'Bottom', '+1 Range', gold=35) # 105gold paid
    party.addEnhancement('Red', 209, 'Bottom', 'Bless', gold=0) # 100gold paid

    # Nov 19
    party.heroBuyItem('Red', 'Minor Stamina Potion')
    party.heroBuyItem('Red', 'Eagle-Eye Goggles')
    party.completeCityEvent(23)
    party.adjustReputation(1) # from City Event

    party.completeRoadEvent(43)
    party.heroAdjustGold('Singularity', 2)
    party.heroAdjustGold('Evan', 2)
    party.heroAdjustGold('Red', 2)
    party.heroAdjustGold('Rabid Cicada', 2)
    party.heroAdjustGold('Ignus', 2)

    party.addTreasureLooted(33, 'Singularity') # Item 19 - Weighted Net
    party.heroFindItem('Singularity', 'Weighted Net')

    party.addScenarioCompleted(68)
    party.heroFindItem('Evan', 'Major Healing Potion')
    party.heroFindItem('Ignus', 'Major Healing Potion')
    party.heroAdjustXP('Rabid Cicada', 17)
    party.heroAdjustXP('Red', 21)
    party.heroAdjustXP('Singularity', 23)
    party.heroAdjustXP('Evan', 19)
    party.heroAdjustXP('Ignus', 14)
    party.heroAdjustGold('Rabid Cicada', 3)
    party.heroAdjustGold('Red', 9)
    party.heroAdjustGold('Singularity', 15)
    party.heroAdjustGold('Evan', 18)
    party.heroAdjustGold('Ignus', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Red', 1)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustCheckmarks('Ignus', 2)

    party.heroGainCheckmarkPerk('Ignus', [remove_2_0, add_1_0_ice, add_1_0_air])
    party.heroLevelUp('Singularity', add_1_roll_at, "Camouflage")

    # Nov 26, 2018
    party.completeCityEvent(43)
    party.unlockCityEvent(61)
    party.heroAdjustGold('Rabid Cicada', -1)
    party.heroAdjustGold('Red', -1)
    party.heroAdjustGold('Singularity', -1)
    party.heroAdjustGold('Evan', -1)
    party.heroAdjustGold('Ignus', -1)

    party.makeSanctuaryDonation('Red')
    party.makeSanctuaryDonation('Singularity')

    party.heroBuyItem('Singularity', 'Hawk Helm')

    party.completeRoadEvent(40)
    party.addTreasureLooted(75, 'Red')

    party.addScenarioCompleted(76)
    party.heroAdjustXP('Rabid Cicada', 23)
    party.heroAdjustXP('Red', 20)
    party.heroAdjustXP('Singularity', 26)
    party.heroAdjustXP('Evan', 23)
    party.heroAdjustXP('Ignus', 17)
    party.heroAdjustGold('Rabid Cicada', 24)
    party.heroAdjustGold('Red', 3)
    party.heroAdjustGold('Singularity', 9)
    party.heroAdjustGold('Evan', 3)
    party.heroAdjustGold('Ignus', 3)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Red', 1)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustCheckmarks('Ignus', 0)

    party.heroLevelUp('Red', add_1_0_refresh_item, 'Catastrophic Bomb')
    party.heroLevelUp('Ignus', add_3_0_air, 'Primal Duality')
    party.heroLevelUp('Rabid Cicada', add_1_roll_invis, 'Stick to the Shadows')
    party.heroLevelUp('Evan', add_1_plus_1_curse, 'Stone Fists')

    # Dec 3, 2018
    party.heroSellItem('Red', 'Horned Helm')
    party.heroSellItem('Rabid Cicada', 'Minor Stamina Potion')
    party.heroBuyItem('Red', 'Piercing Bow')
    party.heroBuyItem('Rabid Cicada', 'Major Stamina Potion')

    party.addScenarioAvailable(72)

    party.completeCityEvent(42)
    party.adjustReputation(1)
    party.addProsperityCheckmark('City Event 42')

    party.completeRoadEvent(46)
    party.addTreasureLooted(12, 'Rabid Cicada')
    party.heroFindItem('Rabid Cicada', 'Magma Waders')
    party.addScenarioCompleted(63)
    party.heroAdjustXP('Rabid Cicada', 19)
    party.heroAdjustXP('Red', 17)
    party.heroAdjustXP('Singularity', 24)
    party.heroAdjustXP('Evan', 17)
    party.heroAdjustXP('Ignus', 16)
    party.heroAdjustGold('Rabid Cicada', 39)
    party.heroAdjustGold('Red', 33)
    party.heroAdjustGold('Singularity', 15)
    party.heroAdjustGold('Evan', 24)
    party.heroAdjustGold('Ignus', 27)
    party.heroAdjustCheckmarks('Rabid Cicada', 2)
    party.heroAdjustCheckmarks('Red', 1)
    party.heroAdjustCheckmarks('Singularity', 2)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustCheckmarks('Ignus', 1)
    
    # Dec 10, 2018
    party.heroGainCheckmarkPerk('Singularity', add_1_roll_at)
    party.heroGainCheckmarkPerk('Red', add_1_0_refresh_item)
    party.heroGainCheckmarkPerk('Evan', add_1_plus_1_immobilize)
    party.completeCityEvent(26)

    #party.makeSanctuaryDonation('Red')
    #party.makeSanctuaryDonation('Singularity')

    party.heroBuyItem('Ignus', 'Major Stamina Potion')

    party.completeRoadEvent(6)
    party.heroAdjustCheckmarks('Rabid Cicada', -1)
    party.heroAdjustCheckmarks('Red', -1)
    party.heroAdjustCheckmarks('Evan', -1)
    party.heroAdjustCheckmarks('Ignus', -1)

    party.addScenarioCompleted(72)
    party.adjustReputation(1)
    party.addProsperityCheckmark('Scenario #72')
    party.heroAdjustXP('Rabid Cicada', 24)
    party.heroAdjustXP('Red', 18)
    party.heroAdjustXP('Evan', 25)
    party.heroAdjustXP('Ignus', 20)
    party.heroAdjustGold('Rabid Cicada', 3)
    party.heroAdjustGold('Red', 9)
    party.heroAdjustGold('Evan', 3)
    party.heroAdjustGold('Ignus', 12)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustCheckmarks('Red', 1)
    party.heroAdjustCheckmarks('Evan', 1)
    party.heroAdjustCheckmarks('Ignus', 2)

    # Dec 17, 2018
    party.heroBuyItem('Rabid Cicada', 'Volatile Bomb')
    party.retireHero(hero3)
    party.addEnhancement('Evan', 73, 'Top', '+1 Attack', gold=125) # 125gold paid
    party.makeSanctuaryDonation('Evan')

    party.unlockHero("Plagueherald")
    party.unlockCityEvent(44) # Spellweaver Retirement
    party.unlockRoadEvent(44) # Spellweaver Retirement
    party.unlockCityEvent(35) # Plagueherald Class Choice
    party.unlockRoadEvent(35) # Plagueherald Class Choice

    hero9 = ch.Character('Playgirl', 'Plagueherald', owner_et, level=1, gold=75, xp=150, quest=520)
    hero9.addOwnerPerk(add_3_roll_poison)
    party.addMember(hero9)
    party.heroLevelUp('Playgirl', ignore_scen_perk_plus_1, 'Under The Skin')
    party.heroLevelUp('Playgirl', add_2_plus_1, 'Fetid Flurry')
    party.heroLevelUp('Playgirl', replace_minus_1_with_plus_1, 'Nigthmarish Affliction')
    party.heroBuyItem('Playgirl', 'Eagle-Eye Goggles')
    party.heroBuyItem('Playgirl', 'Heater Shield')
    party.heroBuyItem('Playgirl', 'Minor Stamina Potion')
    party.heroBuyItem('Playgirl', 'Minor Power Potion')

    party.makeSanctuaryDonation('Red')
    party.makeSanctuaryDonation('Singularity')
    party.makeSanctuaryDonation('Rabid Cicada')
    party.completeCityEvent(35)
    party.addProsperityCheckmark('City Event #35')

    party.completeRoadEvent(14)

    party.addTreasureLooted(1, 'Playgirl')
    party.addItemDesign(82)

    party.addScenarioCompleted(16)
    party.addScenarioAvailable(24)
    party.addScenarioAvailable(25)

    party.heroAdjustXP('Rabid Cicada', 19)
    party.heroAdjustXP('Red', 17)
    party.heroAdjustXP('Playgirl', 16)
    party.heroAdjustXP('Singularity', 20)
    party.heroAdjustGold('Rabid Cicada', 15)
    party.heroAdjustGold('Red', 3)
    party.heroAdjustGold('Playgirl', 9)
    party.heroAdjustGold('Singularity', 3)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Red', 2)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Singularity', 1)

    # Play Session - Dec 26, 2018
    party.heroLevelUp('Singularity', add_1_plus_1_wound, 'Crashing Wave')
    party.completeCityEvent(1)
    party.adjustReputation(1)
    party.makeSanctuaryDonation('Singularity')
    party.completeRoadEvent(12)
    party.adjustReputation(1)

    party.addScenarioCompleted(7)
    party.addScenarioAvailable(20)

    party.heroAdjustXP('Rabid Cicada', 17)
    party.heroAdjustXP('Ignus', 21)
    party.heroAdjustXP('Playgirl', 19)
    party.heroAdjustXP('Singularity', 27)
    party.heroAdjustGold('Rabid Cicada', 12)
    party.heroAdjustGold('Ignus', 44)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustGold('Singularity', 20)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustCheckmarks('Ignus', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Singularity', 1)

    party.addScenarioBlocked(35)
    party.addScenarioBlocked(36)

    # Solo Scenario - Quartermaster
    party.heroAdjustXP('Red', 15)
    party.heroAdjustGold('Red', 12)
    party.heroFindItem('Red', 'Utility Belt')

    # Play Session - Jan ?, 2019
    party.heroGainCheckmarkPerk('Ignus', add_3_0_earth)
    party.heroLevelUp('Rabid Cicada', add_2_roll_muddle, 'Stiletto Storm')
    party.heroGainCheckmarkPerk('Rabid Cicada', add_2_roll_poison)
    party.heroGainCheckmarkPerk('Singularity', add_1_0_stun)

    party.unlockCityEvent(80) # Town Records - Oozing Grove
    
    party.retireHero(hero7)
    party.makeSanctuaryDonation('Red')
    party.addEnhancement('Red', 214, 'Bottom', '+1 Shield', gold=100)
    party.addEnhancement('Red', 210, 'Top', '+1 Move', gold=30)

    party.unlockHero("Nightshroud")
    party.unlockCityEvent(49) # Quartermaster Retirement
    party.unlockRoadEvent(49) # Quartermaster Retirement
    party.unlockCityEvent(34) # Nightshroud Class Choice
    party.unlockRoadEvent(34) # Nightshroud Class Choice

    hero10 = ch.Character('Hayha', 'Nightshroud', owner_dp, level=1, gold=90, xp=210, quest=518)
    hero10.addOwnerPerk(ignore_scen_perk_2_plus_1)
    hero10.addOwnerPerk(remove_2_minus_1)
    party.addMember(hero10)
    party.heroLevelUp('Hayha', add_1_minus_1_dark, 'Prepare for the Kill')
    party.heroLevelUp('Hayha', add_1_minus_1_dark, 'Terror Blade')
    party.heroLevelUp('Hayha', replace_minus_1_dark_with_plus_1_dark, 'Grim Sustenance')
    party.heroLevelUp('Hayha', replace_minus_1_dark_with_plus_1_dark, 'Black Arrow')
    party.addEnhancement("Hayha", 269, 'Bottom', '+1 Move', gold=30)
    party.addEnhancement("Hayha", 273, 'Bottom', '+1 Move', gold=55)

    # Jan 2, 2019
    party.heroBuyItem('Singularity', 'Ring of Haste')

    party.completeCityEvent(80)
    party.adjustReputation(-2)

    party.completeRoadEvent(10)
    party.unlockCityEvent(71)

    party.addTreasureLooted(16, 'Singularity')
    party.addTreasureLooted(36, 'Hayha')
    party.addItemDesign(96) # Rocket Boots
    party.addScenarioCompleted(66)
    party.addGlobalAchievement('Ancient Technology')
    
    party.heroAdjustXP('Rabid Cicada', 21)
    party.heroAdjustXP('Hayha', 21)
    party.heroAdjustXP('Singularity', 30)
    party.heroAdjustGold('Rabid Cicada', 4)
    party.heroAdjustGold('Hayha', 32)
    party.heroAdjustGold('Singularity', 26)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustCheckmarks('Hayha', 0)
    party.heroAdjustCheckmarks('Singularity', 0)
    
    # Solo Scenario - Doomstalker
    party.heroAdjustXP('Singularity', 17)
    party.heroAdjustGold('Singularity', 16)
    party.heroFindItem('Singularity', 'Cloak of the Hunter')
    party.heroSellItem('Singularity', 'Cloak of the Hunter')

    # Jan 7 Session
    party.heroLevelUp('Singularity', ignore_scen_perk, 'Darkened Skies')
    party.heroSellItem('Singularity', 'Minor Power Potion')
    party.heroSellItem('Singularity', 'Minor Stamina Potion')
    party.heroBuyItem('Singularity', 'Major Power Potion')
    party.heroBuyItem('Singularity', 'Major Stamina Potion')
    party.heroBuyItem('Ignus', 'Tower Shield')

    party.completeCityEvent(61)
    party.heroFindItem('Hayha', 'Giant Remote Spider')
    party.heroBuyItem('Hayha', 'Minor Stamina Potion')
    party.heroBuyItem('Hayha', 'Boots of Striding')
    party.makeSanctuaryDonation('Singularity')

    party.addTreasureLooted(69, 'Singularity')
    party.heroFindItem('Singularity', 'Robes of Summoning')

    party.addScenarioCompleted(31)
    party.addGlobalAchievement('Artifact: Cleansed')
    party.addScenarioAvailable(37)
    party.addScenarioAvailable(38)
    party.addScenarioAvailable(39)
    party.addScenarioAvailable(43)
    
    party.heroSellItem('Singularity', 'Robes of Summoning')
    party.heroAdjustXP('Ignus', 19)
    party.heroAdjustXP('Hayha', 25)
    party.heroAdjustXP('Singularity', 27)
    party.heroAdjustXP('Playgirl', 16)
    party.heroAdjustGold('Ignus', 16)
    party.heroAdjustGold('Hayha', 20)
    party.heroAdjustGold('Singularity', 12)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustCheckmarks('Ignus', 0)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Singularity', 0)
    party.heroAdjustCheckmarks('Playgirl', 1)

    party.heroLevelUp('Ignus', add_3_0_ice, 'Obsidian Shards')

    # Jan 14, 2019 - Session
    party.heroBuyItem('Hayha', 'Minor Mana Potion')
    party.heroBuyItem('Ignus', 'Moon Earring')

    party.completeCityEvent(71)
    party.heroAdjustCheckmarks('Ignus', -1)
    party.heroAdjustCheckmarks('Hayha', -1)
    party.heroAdjustCheckmarks('Singularity', -1)
    party.heroAdjustCheckmarks('Playgirl', -1)
    party.heroAdjustCheckmarks('Rabid Cicada', -1)

    party.completeRoadEvent(49)
    party.addScenarioAvailable(80)
    party.heroAdjustGold('Ignus', 5)
    party.heroAdjustGold('Hayha', 5)
    party.heroAdjustGold('Singularity', 5)
    party.heroAdjustGold('Playgirl', 5)
    party.heroAdjustGold('Rabid Cicada', 5)

    party.addTreasureLooted(35, 'Hayha')
    party.heroFindItem('Hayha', 'Drakescale Boots')

    party.addScenarioCompleted(43)
    party.addGlobalAchievement('Water Breathing')

    party.heroAdjustXP('Ignus', 18)
    party.heroAdjustXP('Hayha', 19)
    party.heroAdjustXP('Singularity', 25)
    party.heroAdjustXP('Playgirl', 18)
    party.heroAdjustXP('Rabid Cicada', 25)
    party.heroAdjustGold('Ignus', 0)
    party.heroAdjustGold('Hayha', 21)
    party.heroAdjustGold('Singularity', 3)
    party.heroAdjustGold('Playgirl', 9)
    party.heroAdjustGold('Rabid Cicada', 33)
    party.heroAdjustCheckmarks('Ignus', 1)
    party.heroAdjustCheckmarks('Hayha', 0)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)


    # Jan 21, 2019 - Session
    party.heroSellItem('Rabid Cicada', 'Winged Shoes')
    party.heroBuyItem('Rabid Cicada', 'Rocket Boots')
    party.heroBuyItem('Playgirl', 'Piercing Bow')
    party.heroSellItem('Hayha', 'Boots of Striding')
    party.heroSellItem('Hayha', 'Drakescale Boots')
    party.heroBuyItem('Hayha', 'Rocket Boots')
    party.makeSanctuaryDonation('Rabid Cicada')

    party.completeCityEvent(70)
    party.adjustReputation(-1)
    party.completeRoadEvent(35)

    party.addTreasureLooted(41, 'Hayha')
    party.heroFindItem('Hayha', 'Black Knife')
    party.addScenarioCompleted(29)
    party.addGlobalAchievement('The Edge of Darkness')

    party.heroAdjustXP('Hayha', 33)
    party.heroAdjustXP('Playgirl', 35)
    party.heroAdjustXP('Rabid Cicada', 35)
    party.heroAdjustGold('Hayha', 21)
    party.heroAdjustGold('Playgirl', 3)
    party.heroAdjustGold('Rabid Cicada', 30)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)

    party.heroLevelUp('Rabid Cicada', add_2_roll_plus_1, 'Watch It Burn')
    party.heroLevelUp('Hayha', remove_2_minus_1, 'Swallowed By Fear')
    party.heroLevelUp('Playgirl', add_2_roll_curse, 'Accelerated End')

    party.heroSellItem('Ignus', 'Major Healing Potion')
    party.heroBuyItem('Hayha', 'Cloak of Invisibility')

    # Play Session 28
    party.completeCityEvent(24)
    party.heroAdjustXP('Hayha', 10)
    party.heroAdjustXP('Playgirl', 10)
    party.heroAdjustXP('Rabid Cicada', 10)
    party.heroAdjustXP('Singularity', 10)
    party.heroAdjustXP('Ignus', 10)

    party.completeRoadEvent(26)

    party.addTreasureLooted(58, 'Singularity')
    party.heroFindItem('Singularity', 'Drakescale Helm')

    party.addScenarioCompleted(25)
    party.addScenarioAvailable(33)
    party.addScenarioAvailable(34)
    party.addPartyAchievement("The Drake's Command")
    party.heroAdjustXP('Hayha', 21)
    party.heroAdjustXP('Playgirl', 18)
    party.heroAdjustXP('Rabid Cicada', 18)
    party.heroAdjustXP('Singularity', 21)
    party.heroAdjustXP('Ignus', 18)
    party.heroAdjustGold('Hayha', 24)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustGold('Rabid Cicada', 16)
    party.heroAdjustGold('Singularity', 20)
    party.heroAdjustGold('Ignus', 8)
    party.heroAdjustCheckmarks('Hayha', 0)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustCheckmarks('Ignus', 1)
    party.heroSellItem('Singularity', 'Drakescale Helm')

    # PLay Session Feb 5
    party.heroLevelUp('Singularity', add_1_plus_2_muddle, 'Lead to Slaughter')
    party.heroLevelUp('Playgirl', replace_minus_1_with_plus_1, 'Black Tides')
    party.heroBuyItem('Ignus', 'Winged Shoes')

    party.completeCityEvent(49)
    party.addProsperityCheckmark('City Event #49')

    party.completeRoadEvent(32)
    party.adjustReputation(-1)

    party.addTreasureLooted(63, 'Singularity')
    party.addItemDesign(74)

    party.addScenarioCompleted(18)
    party.addScenarioAvailable(14)
    party.addScenarioAvailable(23)
    party.addScenarioAvailable(26)
    party.addScenarioAvailable(43)
    party.heroAdjustXP('Hayha', 20)
    party.heroAdjustXP('Playgirl', 15)
    party.heroAdjustXP('Rabid Cicada', 20)
    party.heroAdjustXP('Singularity', 30)
    party.heroAdjustXP('Ignus', 20)
    party.heroAdjustGold('Hayha', 72)
    party.heroAdjustGold('Playgirl', 0)
    party.heroAdjustGold('Rabid Cicada', 4)
    party.heroAdjustGold('Singularity', 4)
    party.heroAdjustGold('Ignus', 28)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 2)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)
    party.heroAdjustCheckmarks('Singularity', 1)
    party.heroAdjustCheckmarks('Ignus', 1)

    # Catch Up from Missed Play Sessions
    party.heroLevelUp("Ignus", add_3_0_fire, 'Eye of the Hurricane')
    party.heroGainCheckmarkPerk("Ignus", add_1_0_at)
    party.heroLevelUp("Hayha", add_2_roll_curse, 'Eyes of Night')
    party.addEnhancement('Hayha', 264, "Top", 'Light', gold=100) # 
    party.heroSellItem("Ignus", "Chainmail")
    party.heroBuyItem("Ignus", "Swordedge Armor")
    party.heroBuyItem("Rabid Cicada", "Falcon Figurine")
    
    party.completeCityEvent(29)
    party.addProsperityCheckmark('City Event #29')
    party.completeRoadEvent(3)
    
    party.addTreasureLooted(72, 'Rabid Cicada')
    party.addItemDesign(116)

    party.addScenarioCompleted(23)
    party.heroAdjustXP('Hayha', 25)
    party.heroAdjustXP('Playgirl', 15)
    party.heroAdjustXP('Rabid Cicada', 0)
    party.heroAdjustXP('Ignus', 19)
    party.heroAdjustGold('Hayha', 20)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustGold('Rabid Cicada', 28)
    party.heroAdjustGold('Ignus', 12)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 1)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Ignus', 0)

    party.retireHero(hero8)
    party.unlockCityEvent(57)
    party.unlockRoadEvent(57)
    party.unlockHero("BeastTyrant")
    party.unlockCityEvent(41)
    party.unlockRoadEvent(41)
    party.addEnhancement("Ignus", 464, 'Bottom', 'Strengthen', gold=125)

    party.heroGainCheckmarkPerk("Hayha", add_1_plus_1_invis)
    party.heroGainCheckmarkPerk("Playgirl", add_1_plus_1_air)
    party.heroGainCheckmarkPerk("Singularity", add_1_plus_1_immobilize)

    hero11 = ch.Character('RatManBearPig', 'BeastTyrant', owner_mc, level=1, gold=90, xp=210, quest=527)
    hero11.addOwnerPerk(remove_2_minus_1)
    hero11.addOwnerPerk(replace_minus_1_with_plus_1)
    party.addMember(hero11)
    party.heroLevelUp('RatManBearPig', replace_minus_1_with_plus_1, 'Energizing Strike')
    party.heroLevelUp('RatManBearPig', replace_minus_1_with_plus_1, 'Unstoppable Beast')
    party.heroLevelUp('RatManBearPig', add_1_plus_1_wound, 'Ancient Ward')
    party.heroLevelUp('RatManBearPig', add_1_plus_1_wound, 'Punch Through')
    party.heroBuyItem('RatManBearPig', 'Major Stamina Potion')
    party.heroBuyItem('RatManBearPig', 'Winged Shoes')
    party.heroBuyItem('RatManBearPig', 'Hawk Helm')

    party.makeSanctuaryDonation('RatManBearPig')
    party.makeSanctuaryDonation('Playgirl')
    party.makeSanctuaryDonation('Singularity')

    party.completeCityEvent(9)
    party.addProsperityCheckmark('City Event #9')
    party.completeRoadEvent(65)
    party.adjustReputation(2)
    party.addGlobalAchievement('Ancient Technology')

    # Scenario #38
    party.addTreasureLooted(29, 'Singularity')
    party.heroFindItem('Singularity', 'Endurance Footwraps') # Item #97

    party.heroAdjustXP('Hayha', 24)
    party.heroAdjustXP('Playgirl', 16)
    party.heroAdjustXP('Rabid Cicada', 0)
    party.heroAdjustXP('RatManBearPig', 21)
    party.heroAdjustXP('Singularity', 0)
    party.heroAdjustGold('Hayha', 12)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustGold('Rabid Cicada', 24)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustGold('Singularity', 8)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Singularity', 0)

    party.heroSellItem('Singularity', 'Endurance Footwraps')
    party.addScenarioCompleted(38)
    party.addPartyAchievement("Redthorn's Aid")
    party.addScenarioAvailable(44)
    party.addScenarioAvailable(48)
    party.adjustReputation(1)

    # Mar 4, 2019 Session
    party.completeCityEvent(22)
    party.adjustReputation(2)
    party.completeRoadEvent(5)
    party.adjustReputation(1)

    party.addTreasureLooted(49, 'Singularity')
    party.addScenarioAvailable(17)

    party.addScenarioCompleted(37)
    party.addPartyAchievement('Through the Trench')
    party.addScenarioAvailable(47)

    party.heroAdjustXP('Hayha', 23)
    party.heroAdjustXP('Playgirl', 12)
    party.heroAdjustXP('RatManBearPig', 26)
    party.heroAdjustXP('Singularity', 0)
    party.heroAdjustGold('Hayha', 32)
    party.heroAdjustGold('Playgirl', 12)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustGold('Singularity', 12)
    party.heroAdjustCheckmarks('Hayha', 0)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Singularity', 1)


    # Scenario 57
    party.heroLevelUp('Hayha', add_1_plus_1_invis, 'Gloom Darts')
    
    party.completeCityEvent(57)
    party.heroAdjustGold('Hayha', -2)
    party.heroAdjustGold('Playgirl', -2)
    party.heroAdjustGold('Rabid Cicada', -2)
    party.heroAdjustGold('RatManBearPig', -2)
    party.heroAdjustGold('Singularity', -2)
    party.addItemDesign(118)
    party.heroSellItem('Hayha', 'Black Knife')
    party.heroSellItem('Hayha', 'Minor Stamina Potion')
    party.heroBuyItem('Hayha', 'Staff of Elements')
    party.heroBuyItem('Hayha', 'Major Stamina Potion')
    
    party.completeRoadEvent(15)
    party.addTreasureLooted(22, 'RatManBearPig')
    party.addItemDesign(93)
    party.addTreasureLooted(2, 'Playgirl')
    party.heroFindItem("Playgirl", "Splintmail")
    
    party.addScenarioCompleted(57)
    party.adjustReputation(1)
    party.addScenarioAvailable(58)
    party.heroAdjustXP('Hayha', 22)
    party.heroAdjustXP('Playgirl', 15)
    party.heroAdjustXP('RatManBearPig', 23)
    party.heroAdjustXP('Singularity', 0)
    party.heroAdjustXP('Rabid Cicada', 0)
    party.heroAdjustGold('Hayha', 32)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustGold('RatManBearPig', 0)
    party.heroAdjustGold('Singularity', 4)
    party.heroAdjustGold('Rabid Cicada', 8)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Singularity', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)

    party.heroLevelUp('RatManBearPig', ignore_scen_perk, 'Blood Hunger')
    party.heroGainCheckmarkPerk('RatManBearPig', add_2_roll_heal1)

    # Matt Solo Attempts
    party.heroAdjustXP('RatManBearPig', 30)
    party.heroAdjustGold('RatManBearPig', 6)
    party.heroSellItem('RatManBearPig', 'Winged Shoes')
    party.heroBuyItem('RatManBearPig', 'Boots of Speed')
    party.heroAdjustXP('RatManBearPig', 31)
    party.heroAdjustGold('RatManBearPig', 6)
    party.heroFindItem('RatManBearPig', 'Staff of Command')

    # Play Session - March 25, 2019
    party.makeSanctuaryDonation('Singularity')
    party.retireHero(hero6)
    party.unlockCityEvent(55)
    party.unlockRoadEvent(55)
    party.unlockHero("Summoner")
    party.addEnhancement("Singularity", 387, 'Bottom', '+1 Move', gold=30)
    party.addEnhancement("Singularity", 396, 'Bottom', '+1 Move', gold=105) # 30 (for +1 Move) + 75 (level 4)
    party.addEnhancement("Singularity", 390, 'Bottom', '+1 Move', gold=30)

    # QUEST ###????!!!!
    party.heroSellItem('Playgirl', 'Minor Stamina Potion')
    party.heroBuyItem('Playgirl', 'Major Stamina Potion')
    hero12 = ch.Character('Snickers', 'Mindthief', owner_ag, level=1, gold=90, xp=210, quest=532)
    hero12.addOwnerPerk(remove_2_minus_1)
    hero12.addOwnerPerk(remove_2_minus_1)
    party.addMember(hero12)
    party.heroLevelUp('Snickers', replace_minus_2_with_0, 'Hostile Takeover')
    party.heroLevelUp('Snickers', ignore_scen_perk, 'Brian Leech')
    party.heroLevelUp('Snickers', add_2_roll_plus_1, 'Pilfer')
    party.heroLevelUp('Snickers', remove_4_0, 'Mass Hysteria')
    party.heroBuyItem('Snickers', 'Minor Stamina Potion')
    party.heroBuyItem('Snickers', 'Boots of Striding')
    party.heroBuyItem('Snickers', 'Cloak of Invisibility')
    party.heroBuyItem('Snickers', 'Stun Powder')
    party.heroBuyItem('Snickers', 'Eagle-Eye Goggles')

    party.makeSanctuaryDonation('Hayha')
    party.completeCityEvent(3)
    party.heroAdjustGold('Hayha', -10)
    party.addGlobalAchievement('Ancient Technology')
    party.heroFindItem('RatManBearPig', 'Curious Gear') # 123
    party.completeRoadEvent(57)
    party.addScenarioCompleted(58)
    party.adjustReputation(2)
    party.heroAdjustXP('Hayha', 20)
    party.heroAdjustXP('Playgirl', 16)
    party.heroAdjustXP('RatManBearPig', 20)
    party.heroAdjustXP('Snickers', 19)
    party.heroAdjustXP('Rabid Cicada', 0)
    party.heroAdjustGold('Hayha', 28)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustGold('RatManBearPig', 8)
    party.heroAdjustGold('Snickers', 20)
    party.heroAdjustGold('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 1)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustCheckmarks('Snickers', 2)
    party.heroAdjustCheckmarks('Rabid Cicada', 1)

    party.retireHero(hero5)
    party.makeSanctuaryDonation('Rabid Cicada')
    party.makeSanctuaryDonation('Snickers')
    
    hero13 = ch.Character('Ragnarok', 'summoner', owner_ks, level=1, gold=105, xp=275, quest=514)
    hero13.addOwnerPerk(remove_2_minus_1)
    party.addMember(hero13)
    party.heroLevelUp('Ragnarok', replace_minus_2_with_0, 'Grasping The Void')
    party.heroLevelUp('Ragnarok', replace_minus_1_with_plus_1, 'Earthen Steed')
    party.heroLevelUp('Ragnarok', replace_minus_1_with_plus_1, 'Divided Mind')
    party.heroLevelUp('Ragnarok', replace_minus_1_with_plus_1, 'Strength In Numbers')
    party.heroLevelUp('Ragnarok', ignore_scen_perk_2_plus_1, 'Endless Spikes')
    party.heroBuyItem('Ragnarok', 'Major Stamina Potion')
    party.heroBuyItem('Ragnarok', 'Boots of Quickness')
    party.unlockCityEvent(33)
    party.unlockRoadEvent(33)

    party.heroLevelUp('RatManBearPig', add_2_roll_heal1, 'Tyrannical Force')
    
    party.completeCityEvent(33)
    party.adjustReputation(2)
    
    party.completeRoadEvent(21)
    
    party.addTreasureLooted(73, 'Hayha')
    party.addItemDesign(91) # Steel Ring

    party.addScenarioCompleted(39)
    party.addPartyAchievement('Across the Divide')
    party.addScenarioAvailable(15)
    party.addScenarioAvailable(46)

    party.heroAdjustXP('Hayha', 37)
    party.heroAdjustXP('RatManBearPig', 38)
    party.heroAdjustXP('Snickers', 34)
    party.heroAdjustXP('Ragnarok', 37)
    party.heroAdjustGold('Hayha', 12)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustGold('Snickers', 28)
    party.heroAdjustGold('Ragnarok', 20)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustCheckmarks('Snickers', 1)
    party.heroAdjustCheckmarks('Ragnarok', 1)

    # Session Apr 8
    party.heroLevelUp('Hayha', add_1_roll_at, 'Angel of Death')
    party.heroGainCheckmarkPerk('Hayha', remove_4_0)
    party.heroGainCheckmarkPerk('Snickers', add_2_roll_plus_1)

    party.completeCityEvent(32)
    party.adjustReputation(1)
    
    # Accidental redo of 32
    party.completeRoadEvent(999)
    party.heroAdjustGold('Hayha', -5)
    party.heroAdjustGold('Playgirl', -5)
    party.heroAdjustGold('Ragnarok', -5)
    party.adjustReputation(1)
    
    party.addTreasureLooted(71, 'Hayha')
    party.addScenarioAvailable(65)

    party.addScenarioCompleted(17)

    party.heroAdjustXP('Hayha', 0)
    party.heroAdjustXP('Playgirl', 17)
    party.heroAdjustXP('Ragnarok', 17)
    party.heroAdjustGold('Hayha', 82)
    party.heroAdjustGold('Playgirl', 40)
    party.heroAdjustGold('Ragnarok', 37)
    party.heroAdjustCheckmarks('Hayha', 1)
    party.heroAdjustCheckmarks('Playgirl', 1)
    party.heroAdjustCheckmarks('Ragnarok', 1)

    # Play Session - Apr 15
    party.heroLevelUp('Playgirl', replace_0_with_plus_2, 'Baneful Hex')
    party.heroSellItem('RatManBearPig', 'Curious Gear')
    party.heroBuyItem('RatManBearPig', 'Ring of Haste')
    party.heroBuyItem('Ragnarok', 'Falcon Figurine')
    party.heroBuyItem('RatManBearPig', 'Moon Earring')

    party.completeCityEvent(38)
    party.addProsperityCheckmark('City Event #38')

    party.completeRoadEvent(13)

    party.addScenarioCompleted(15)

    party.heroAdjustXP('Snickers', 50)
    party.heroAdjustXP('Playgirl', 38)
    party.heroAdjustXP('Ragnarok', 46)
    party.heroAdjustXP('RatManBearPig', 52)
    party.heroAdjustGold('Snickers', 16)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustGold('Ragnarok', 16)
    party.heroAdjustGold('RatManBearPig', 8)
    party.heroAdjustCheckmarks('Snickers', 0)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)

    # Next Session
    party.heroLevelUp('RatManBearPig', add_2_roll_heal1, 'Last Out')
    party.heroLevelUp('Playgirl', replace_0_with_plus_2, 'Spreading Scourge')
    party.heroLevelUp('Ragnarok', add_1_plus_2, 'Negative Energy')
    party.heroLevelUp('Snickers', replace_2_plus_1_with_2_plus_2, 'Corrupting Embrace')
    party.heroBuyItem('Hayha', 'Empowering Talisman')

    party.completeCityEvent(46)
    party.heroAdjustGold('Hayha', -5)
    party.heroAdjustGold('Playgirl', -5)
    party.heroAdjustGold('Ragnarok', -5)
    party.heroAdjustGold('Snickers', -5)
    party.heroAdjustGold('RatManBearPig', -5)
    party.adjustReputation(1)
    party.makeSanctuaryDonation('Hayha')

    party.completeRoadEvent(44)
    party.addScenarioAvailable(90)

    party.addTreasureLooted(66, 'Hayha')
    party.heroFindItem('Ragnarok', 'Volatile Bomb')
    
    party.addScenarioCompleted(26)
    party.addPartyAchievement('Following Clues')
    party.addScenarioAvailable(22)
    party.adjustReputation(1)
    party.addProsperityCheckmark('Scenario 26', cnt=2)

    party.heroAdjustXP('Snickers', 27)
    party.heroAdjustXP('Playgirl', 19)
    party.heroAdjustXP('Ragnarok', 27)
    party.heroAdjustXP('RatManBearPig', 26)
    party.heroAdjustXP('Hayha', 0)
    party.heroAdjustGold('Snickers', 22)
    party.heroAdjustGold('Playgirl', 18)
    party.heroAdjustGold('Ragnarok', 22)
    party.heroAdjustGold('RatManBearPig', 22)
    party.heroAdjustGold('Hayha', 30)
    party.heroAdjustCheckmarks('Snickers', 0)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Hayha', 1)

    # Next Play Session
    party.completeCityEvent(13)
    party.heroAdjustGold('Hayha', -3)
    party.heroAdjustGold('Snickers', -3)
    party.heroAdjustGold('RatManBearPig', -3)
    party.makeSanctuaryDonation('Hayha')
    party.makeSanctuaryDonation('Snickers')

    party.completeRoadEvent(22)
    party.unlockCityEvent(74)

    party.addScenarioCompleted(65)
    party.addGlobalAchievement('Ancient Technology')
    party.addItemDesign(112)
    party.heroAdjustXP('Snickers', 19)
    party.heroAdjustXP('RatManBearPig', 28)
    party.heroAdjustXP('Hayha', 0)
    party.heroAdjustGold('Snickers', 28)
    party.heroAdjustGold('RatManBearPig', 28)
    party.heroAdjustGold('Hayha', 12)
    party.heroAdjustCheckmarks('Snickers', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Hayha', 0)


    party.heroLevelUp('RatManBearPig', replace_0_with_plus_2, 'Jaws of Death')
    party.heroGainCheckmarkPerk('RatManBearPig', replace_0_with_plus_2)

    party.retireHero(hero10)
    party.unlockCityEvent(51)
    party.unlockRoadEvent(51)
    party.retireHero(hero12)
    party.unlockCityEvent(47)
    party.unlockRoadEvent(47)
    party.unlockHero('Soothsinger')

    party.addEnhancement('Hayha', 273, 'Bottom', 'Create Any Element', gold=250)
    party.addEnhancement('Snickers', 153, 'Top', '+1 Move', gold=30)
    party.addEnhancement('Snickers', 154, 'Bottom', 'Poison', gold=75)
    party.addEnhancement('Snickers', 149, 'Bottom', '+1 Move', gold=30)
    
    hero14 = ch.Character('Drop', 'soothsinger', owner_ag, level=1, gold=105, xp=275, quest=519)
    hero14.addOwnerPerk(remove_2_minus_1)
    hero14.addOwnerPerk(remove_2_minus_1)
    hero14.addOwnerPerk(remove_1_minus_2)
    party.addMember(hero14)
    party.heroLevelUp('Drop', replace_2_plus_1_with_1_plus_4, 'Change Tempo')
    party.heroLevelUp('Drop', replace_2_plus_1_with_1_plus_4, 'Echoing Aria')
    party.heroLevelUp('Drop', replace_0_with_plus_3_muddle, 'Disorienting Dirge')
    party.heroLevelUp('Drop', replace_0_with_plus_2_poison, 'Mobilizing Measure')
    party.heroLevelUp('Drop', replace_0_with_plus_2_wound, 'Provoke Terror')
    party.heroBuyItem('Drop', 'Cloak of Invisibility')
    party.heroBuyItem('Drop', 'Boots of Striding')
    party.heroBuyItem('Drop', 'Giant Remote Spider')
    party.heroBuyItem('Drop', 'Minor Stamina Potion')
    party.unlockCityEvent(37)
    party.unlockRoadEvent(37)

    hero15 = ch.Character('Bucky', 'elementalist', owner_dp, level=1, gold=105, xp=275, quest=513)
    hero15.addOwnerPerk(remove_2_minus_1)
    hero15.addOwnerPerk(remove_2_minus_1)
    hero15.addOwnerPerk([remove_2_0, add_1_0_fire, add_1_0_earth])
    party.addMember(hero15)
    party.heroLevelUp('Bucky', [remove_2_0, add_1_0_ice, add_1_0_air], 'Crystallizing Blast')
    party.heroLevelUp('Bucky', add_3_0_fire, 'Boiling Arc')
    party.heroLevelUp('Bucky', add_3_0_earth, 'Gravel Vortex')
    party.heroLevelUp('Bucky', add_3_0_ice, 'Obsidian Shards')
    party.heroLevelUp('Bucky', add_3_0_air, 'Simulacrum')
    party.heroBuyItem('Bucky', 'Rocket Boots')
    party.heroBuyItem('Bucky', 'Minor Stamina Potion')

    # Play Session May 6
    party.heroBuyItem('RatManBearPig', 'Robes of Summoning')
    party.completeCityEvent(12)
    party.heroAdjustGold('Bucky', 10)
    party.heroAdjustGold('Ragnarok', 10)
    party.heroAdjustGold('RatManBearPig', 10)
    party.heroAdjustCheckmarks('Bucky', -1)
    party.heroAdjustCheckmarks('Ragnarok', -1)
    party.heroAdjustCheckmarks('RatManBearPig', -1)
    party.adjustReputation(1)

    party.completeRoadEvent(51)
    party.heroFindItem('Bucky', 'Black Card')
    
    party.addTreasureLooted(19)
    party.addItemDesign(94)

    party.addScenarioCompleted(90)
    party.heroAdjustXP('Bucky', 17)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 21)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustGold('RatManBearPig', 20)
    party.heroAdjustGold('Ragnarok', 8)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Ragnarok', 1)
    party.heroFindItem('RatManBearPig', 'Black Censer')
    party.heroSellItem('Bucky', 'Black Card')

    # May 13 Play Session
    party.heroBuyItem('Bucky', 'Minor Mana Potion')
    party.heroBuyItem('Bucky', 'Moon Earring')
    party.heroBuyItem('Bucky', 'Staff of Elements')
    party.heroSellItem('RatManBearPig', 'Black Censer')
    party.heroBuyItem('RatManBearPig', 'Sun Earring')
    party.heroLevelUp('Ragnarok', [add_1_roll_dark, add_1_roll_earth], 'Otherworldly Rage')
    party.heroBuyItem('Ragnarok', 'Ring of Skulls')
    party.makeSanctuaryDonation('RatManBearPig')
    
    party.completeCityEvent(47)
    party.adjustReputation(-1)
    party.addScenarioAvailable(87)
    party.addPartyAchievement("The Poison's Source")

    party.completeRoadEvent(24)
    party.addScenarioAvailable(82)
    party.heroAdjustGold('Bucky', 2)
    party.heroAdjustGold('RatManBearPig', 2)
    party.heroAdjustGold('Ragnarok', 2)
    party.heroAdjustGold('Drop', 2)
    party.heroAdjustGold('Playgirl', 2)

    party.addTreasureLooted(70)
    party.addScenarioAvailable(69)

    party.addScenarioCompleted(24)
    party.addScenarioAvailable(30)
    party.addScenarioAvailable(32)
    party.addPartyAchievement("The Voice's Command")

    party.heroAdjustXP('Bucky', 18)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 23)
    party.heroAdjustXP('Drop', 25)
    party.heroAdjustXP('Playgirl', 18)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustGold('RatManBearPig', 0)
    party.heroAdjustGold('Ragnarok', 8)
    party.heroAdjustGold('Drop', 8)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustCheckmarks('Playgirl', 0)

    # May 20, 2019
    party.heroSellItem('Playgirl', 'Heater Shield')
    party.heroSellItem('Playgirl', 'Splintmail')
    party.heroBuyItem('Playgirl', 'Skullbane Axe')
    party.heroBuyItem('Playgirl', 'Cloak of Invisibility')
    party.heroBuyItem('Playgirl', 'Major Healing Potion')
    party.heroBuyItem('Ragnarok', 'Studded Leather')
    
    hero16 = ch.Character('Trog-dor', 'cragheart', owner_michael, level=1, gold=105, xp=275, quest=521)
    party.addMember(hero16)
    party.heroLevelUp('Trog-dor', replace_minus_1_with_plus_1, 'Explosive Punch')
    party.heroLevelUp('Trog-dor', replace_minus_1_with_plus_1, 'Clear the Way')
    party.heroLevelUp('Trog-dor', replace_minus_1_with_plus_1, 'Rock Slide')
    party.heroLevelUp('Trog-dor', [add_1_minus_2, add_2_plus_2], 'Stone Pummel')
    party.heroLevelUp('Trog-dor', add_2_roll_earth, 'Cataclysm')
    #party.heroBuyItem('Trog-dor', 'Major Stamina Potion')
    #party.heroBuyItem('Trog-dor', 'Tower Shield')
    #party.heroBuyItem('Trog-dor', 'Horned Helm')
    #party.heroBuyItem('Trog-dor', 'Boots of Striding')

    party.makeSanctuaryDonation('RatManBearPig')
    party.completeCityEvent(78)
    party.heroAdjustGold('Trog-dor', 1)
    party.heroAdjustGold('RatManBearPig', 1)
    party.heroAdjustGold('Ragnarok', 1)
    party.heroAdjustGold('Drop', 1)
    party.heroAdjustGold('Playgirl', 1)
    party.addScenarioAvailable(94)

    party.completeRoadEvent(42)

    party.addScenarioCompleted(33)
    party.addScenarioAvailable(40)
    party.addPartyAchievement("The Voice's Treasure")
    party.addPartyAchievement("The Drake's Treasure")
    party.heroAdjustXP('Trog-dor', 28)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 26)
    party.heroAdjustXP('Drop', 36)
    party.heroAdjustXP('Playgirl', 15)
    party.heroAdjustGold('Trog-dor', 0)
    party.heroAdjustGold('RatManBearPig', 0)
    party.heroAdjustGold('Ragnarok', 6)
    party.heroAdjustGold('Drop', 15)
    party.heroAdjustGold('Playgirl', 9)
    party.heroAdjustCheckmarks('Trog-dor', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustCheckmarks('Playgirl', 1)


    # Play Session - May 27
    party.completeCityEvent(5)
    party.heroAdjustCheckmarks('Trog-dor', -1)
    party.heroAdjustCheckmarks('RatManBearPig', -1)
    party.heroAdjustCheckmarks('Ragnarok', -1)
    party.heroAdjustCheckmarks('Bucky', -1)
    party.heroAdjustCheckmarks('Playgirl', -1)
    party.adjustReputation(1)
    party.addProsperityCheckmark('City Event 5')
    

    party.completeRoadEvent(20)
    # Experience gain accounted for in final total

    party.addScenarioCompleted(69)
    party.heroAdjustXP('Trog-dor', 31)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 32)
    party.heroAdjustXP('Bucky', 25)
    party.heroAdjustXP('Playgirl', 19)
    party.heroAdjustGold('Trog-dor', 23)
    party.heroAdjustGold('RatManBearPig', 0)
    party.heroAdjustGold('Ragnarok', 43)
    party.heroAdjustGold('Bucky', 35)
    party.heroAdjustGold('Playgirl', 19)
    party.heroAdjustCheckmarks('Trog-dor', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 2)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Playgirl', 1)
 
    party.heroBuyItem('Bucky', 'Hawk Helm')
    party.heroGainCheckmarkPerk('RatManBearPig', add_1_plus_1_immobilize)


    # Play Session - June 3
    party.heroLevelUp('Ragnarok', add_1_plus_2, 'Horned Majesty')
    party.completeCityEvent(44)
    party.heroAdjustGold('Trog-dor', 2)
    party.heroAdjustGold('RatManBearPig', 2)
    party.heroAdjustGold('Ragnarok', 2)
    party.heroAdjustGold('Drop', 2)
    party.heroAdjustGold('Bucky', 2)
    party.adjustReputation(1)

    party.unlockCityEvent(76)
    party.unlockRoadEvent(67)

    party.completeRoadEvent(37)

    party.heroFindItem('Drop', 'Helm of the Mountain')
    party.heroFindItem('Drop', 'Mountain Hammer')

    party.addScenarioCompleted(82)
    party.adjustReputation(-1)
    party.addProsperityCheckmark('Scen 82', -2)
    party.heroAdjustXP('Trog-dor', 19)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustXP('Bucky', 21)
    party.heroAdjustXP('Drop', 27)
    party.heroAdjustGold('Trog-dor', 12)
    party.heroAdjustGold('RatManBearPig', 8)
    party.heroAdjustGold('Ragnarok', 28)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustGold('Drop', 52)
    party.heroAdjustCheckmarks('Trog-dor', 2)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustCheckmarks('Ragnarok', 1)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustCheckmarks('Drop', 1)

    party.heroSellItem('Drop', 'Helm of the Mountain')
    party.heroSellItem('Drop', 'Mountain Hammer')

    # June 10 - Session
    party.heroLevelUp('Bucky', replace_minus_1_with_plus_1, 'Vengeance')
    party.heroLevelUp('Drop', replace_1_minus_1_with_1_stun, 'Nightmare Serenade')
    party.heroGainCheckmarkPerk('Drop', add_2_roll_curse)
    party.heroGainCheckmarkPerk('Playgirl', add_1_roll_stun)
    party.heroBuyItem('Ragnarok', 'Stun Powder')
    party.heroBuyItem('Ragnarok', 'Mountain Hammer')
    party.heroBuyItem('Ragnarok', 'Heater Shield')
    party.heroBuyItem('Bucky', 'Flea-Bitten Shawl')
    party.heroBuyItem('Bucky', 'Minor Power Potion')

    party.completeCityEvent(40)
    party.adjustReputation(1)
    party.heroFindItem('Drop', 'Sacrificial Robes')
    party.heroSellItem('Drop', 'Sacrificial Robes')
    
    party.completeRoadEvent(30)

    party.addScenarioCompleted(44)
    party.heroAdjustXP('Playgirl', 16)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustXP('Bucky', 22)
    party.heroAdjustXP('Drop', 34)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustGold('RatManBearPig', 8)
    party.heroAdjustGold('Ragnarok', 28)
    party.heroAdjustGold('Bucky', 12)
    party.heroAdjustGold('Drop', 24)
    party.heroAdjustCheckmarks('Playgirl', 1)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Ragnarok', 1)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustCheckmarks('Drop', 2)

    # June 17 - Session
    party.addScenarioAvailable(73) # from reading Town Records
    party.heroGainCheckmarkPerk('Ragnarok', [add_1_roll_fire, add_1_roll_air])
    party.heroSellItem('Ragnarok', 'Mountain Hammer')
    party.heroSellItem('Ragnarok', 'Heater Shield')
    party.heroBuyItem('Ragnarok', 'Tower Shield')
    party.heroBuyItem('Ragnarok', 'Scroll of Healing')
    party.heroBuyItem('Drop', 'Minor Healing Potion')
    party.heroSellItem('Bucky', 'Minor Power Potion')
    party.heroBuyItem('Bucky', 'Sun Earring')

    party.completeCityEvent(76)
    party.addScenarioAvailable(74)
    party.addPartyAchievement('High Sea Escort')

    party.completeRoadEvent(47)

    party.addTreasureLooted(57, 'Drop')
    party.heroAdjustGold('Drop', 15)
    party.addTreasureLooted(18, 'Bucky')
    party.heroAdjustGold('Bucky', 15)
    party.addScenarioCompleted(47)
    party.addScenarioAvailable(51)
    party.addGlobalAchievement('End of Corruption')
    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustXP('Bucky', 20)
    party.heroAdjustXP('Drop', 24)
    party.heroAdjustGold('Ragnarok', 0)
    party.heroAdjustGold('Bucky', 0)
    party.heroAdjustGold('Drop', 12)
    party.heroAdjustCheckmarks('Ragnarok', 1)
    party.heroAdjustCheckmarks('Bucky', 2)
    party.heroAdjustCheckmarks('Drop', 2)
    party.heroSellItem('Drop', 'Minor Healing Potion')

    # Jun 24, 2019
    party.heroLevelUp('Drop', add_3_roll_plus_1, 'Tranquil Trill')
    party.heroLevelUp('Playgirl', add_1_plus_1_air, 'Mass Extinction')
    party.heroGainCheckmarkPerk('Drop', add_2_roll_curse)
    party.heroGainCheckmarkPerk('Bucky', replace_0_with_plus_2)

    party.completeCityEvent(74)
    party.adjustReputation(1)
    party.completeRoadEvent(41)
    
    party.addTreasureLooted(20, 'Bucky')
    party.addItemDesign(80)

    party.addScenarioCompleted(74)
    party.addProsperityCheckmark('Scenario 74 Completion', 2)

    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustXP('Bucky', 19)
    party.heroAdjustXP('Drop', 24)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Ragnarok', 34)
    party.heroAdjustGold('Bucky', 26)
    party.heroAdjustGold('Drop', 10)
    party.heroAdjustGold('RatManBearPig', 14)
    party.heroAdjustGold('Playgirl', 34)
    party.heroAdjustCheckmarks('Ragnarok', 0)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Drop', 2)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Playgirl', 1)

    party.heroGainCheckmarkPerk('Drop', replace_0_with_plus_1_disarm)

    # Play Session - July 1
    party.heroLevelUp('Trog-dor', ignore_scen_perk, 'Meteor')
    party.heroBuyItem('Trog-dor', 'Tremor Blade')

    party.completeCityEvent(37)
    party.addProsperityCheckmark('City Event #37', 1)
    party.completeRoadEvent(33)
    
    party.addScenarioCompleted(30)
    party.addPartyAchievement('The Scepter and the Voice')

    party.heroAdjustXP('Bucky', 17)
    party.heroAdjustXP('Trog-dor', 20)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Bucky', 42)
    party.heroAdjustGold('Trog-dor', 26)
    party.heroAdjustGold('RatManBearPig', 22)
    party.heroAdjustGold('Playgirl', 10)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustCheckmarks('Trog-dor', 1)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Playgirl', 2)

    party.heroGainCheckmarkPerk('Trog-dor', add_1_plus_2_muddle)

    # Play Session - Jul 8, 2019
    party.heroLevelUp('Bucky', replace_0_with_plus_2, 'Pragmatic Reinforcement')
    party.heroSellItem('Bucky', 'Minor Mana Potion')
    party.heroBuyItem('Bucky', 'Cloak of Pockets')
    party.heroBuyItem('Bucky', 'Major Mana Potion')
    party.heroBuyItem('Bucky', 'Major Power Potion')

    party.makeSanctuaryDonation('RatManBearPig')
    
    party.completeCityEvent(55)
    party.addProsperityCheckmark('City Event #55')
    party.heroBuyItem('RatManBearPig', 'Ring of Brutality')

    party.completeRoadEvent(67)
    party.addProsperityCheckmark('City Event #67')
    
    party.addTreasureLooted(47, 'Bucky')
    party.heroFindItem('Bucky', 'Steam Armor')

    party.addScenarioCompleted(40)
    party.heroAdjustXP('Bucky', 25)
    party.heroAdjustXP('Drop', 35)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustGold('Bucky', 16)
    party.heroAdjustGold('Drop', 44)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustGold('Ragnarok', 28)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustCheckmarks('RatManBearPig', 1)
    party.heroAdjustCheckmarks('Ragnarok', 0)

    party.addGlobalAchievement('Ancient Technology')
    party.addScenarioAvailable(41)

    # July 15, 2019 Play Session
    party.heroSellItem('Bucky', 'Flea-Bitten Shawl')
    party.heroSellItem('Bucky', 'Steam Armor')

    party.completeCityEvent(41)

    party.completeRoadEvent(2)
    
    party.addScenarioCompleted(73)
    party.adjustReputation(1)

    party.heroAdjustXP('Bucky', 25)
    party.heroAdjustXP('Drop', 32)
    party.heroAdjustXP('Trog-dor', 23)
    party.heroAdjustXP('Ragnarok', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Bucky', 16)
    party.heroAdjustGold('Drop', 28)
    party.heroAdjustGold('Trog-dor', 0)
    party.heroAdjustGold('Ragnarok', 8)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustCheckmarks('Trog-dor', 1)
    party.heroAdjustCheckmarks('Ragnarok', 2)
    party.heroAdjustCheckmarks('Playgirl', 1)


    # July 22, 2019 Play Session
    party.heroLevelUp('Drop', replace_0_with_plus_2_curse, 'Captivating Performance')

    party.retireHero(hero13)
    party.makeSanctuaryDonation('Ragnarok')
    party.addEnhancement('Ragnarok', 236, 'Top', '+1 Move', gold=100)
    party.unlockCityEvent(50)
    party.unlockRoadEvent(50)

    hero17 = ch.Character('JarJar', 'scoundrel', owner_ks, level=1, gold=120, xp=345, quest=529)
    hero17.addOwnerPerk(ignore_scen_perk)
    hero17.addOwnerPerk(remove_2_minus_1)
    hero17.addOwnerPerk(replace_minus_2_with_0)
    party.addMember(hero17)
    party.heroLevelUp('JarJar', remove_2_minus_1, 'Open Wound')
    party.heroLevelUp('JarJar', replace_minus_1_with_plus_1, 'Hidden Daggers')
    party.heroLevelUp('JarJar', remove_4_0, 'Flurry of Blades')
    party.heroLevelUp('JarJar', replace_0_with_plus_2, 'Visage of the Inevitable')
    party.heroLevelUp('JarJar', replace_0_with_plus_2, 'Buring Oil')
    party.heroLevelUp('JarJar', add_1_roll_invis, 'Stick to the Shadows')
    party.heroBuyItem('JarJar', 'Heater Shield')
    party.heroBuyItem('JarJar', 'Rocket Boots')
    party.heroBuyItem('JarJar', 'Major Stamina Potion')
    party.heroBuyItem('JarJar', 'Minor Power Potion')

    party.completeCityEvent(2)
    party.heroAdjustGold('Bucky', -10)

    party.completeRoadEvent(55)

    #party.addTreasureLooted('', 0)
    #party.addScenarioCompleted()
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 16)
    party.heroAdjustGold('JarJar', 12)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustXP('Bucky', 13)
    party.heroAdjustGold('Bucky', 16)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustXP('RatManBearPig', 0)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Playgirl', 8)
    party.heroAdjustCheckmarks('Playgirl', 0)
    #party.addGlobalAchievement('')
    #party.addPartyAchievement('')
    #party.addScenarioAvailable(0)
    #party.adjustReputation(0)

    party.retireHero(hero11)
    party.makeSanctuaryDonation('RatManBearPig')
    party.addEnhancement('RatManBearPig', 494, 'Top', '+1 Attack', gold=175)
    party.unlockHero("Sunkeeper")
    party.unlockCityEvent(58)
    party.unlockRoadEvent(58)

    hero18 = ch.Character('Nova', 'sunkeeper', owner_mc, level=1, gold=120, xp=345, quest=515)
    hero18.addOwnerPerk(remove_2_minus_1)
    hero18.addOwnerPerk(remove_2_minus_1)
    hero18.addOwnerPerk(remove_4_0)
    party.addMember(hero18)
    party.unlockCityEvent(31)
    party.unlockRoadEvent(31)
    party.heroLevelUp('Nova', ignore_item_perk_add_2_plus_1, 'Practical Plans')
    party.heroLevelUp('Nova', ignore_scen_perk, 'Mobilizing Axiom')
    party.heroLevelUp('Nova', add_2_roll_shield1, 'Righteous Strength')
    party.heroLevelUp('Nova', add_2_roll_light, 'Scales of Justice')
    party.heroLevelUp('Nova', add_2_roll_light, 'Supportive Chant')
    party.heroLevelUp('Nova', add_2_roll_heal1, 'Bright Aegis')
    party.heroBuyItem('Nova', 'Minor Stamina Potion')
    party.heroBuyItem('Nova', 'Iron Helmet')
    party.addEnhancement('Nova', 184, 'Bottom', '+1 Shield', gold=100)

    # Play Session - July 28, 2019
    party.heroBuyItem('Bucky', 'Doomed Compass')
    party.heroGainCheckmarkPerk('Playgirl', add_1_plus_1_air)
    
    party.completeCityEvent(7)
    party.heroAdjustGold('JarJar', 5)
    party.heroAdjustGold('Bucky', 5)
    party.heroAdjustGold('Playgirl', 5)
    party.heroAdjustGold('Nova', 5)
    party.heroAdjustGold('Drop', 5)
    party.adjustReputation(-1)

    party.completeRoadEvent(18)

    #party.addTreasureLooted('', 0)
    party.addScenarioCompleted(80)
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 31)
    party.heroAdjustGold('JarJar', 28)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustXP('Bucky', 36)
    party.heroAdjustGold('Bucky', 8)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustXP('Nova', 31)
    party.heroAdjustGold('Nova', 20)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Playgirl', 16)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 20)
    party.heroAdjustCheckmarks('Drop', 0)
    #party.addGlobalAchievement('')
    #party.addPartyAchievement('')
    #party.addScenarioAvailable(0)
    #party.adjustReputation(0)


    # Play Session - August 5, 2019
    party.heroBuyItem('Nova', 'Swordedge Armor')
    
    party.completeCityEvent(51)

    party.completeRoadEvent(58)

    #party.addTreasureLooted('', 0)
    party.addScenarioCompleted(32)
    party.addScenarioAvailable(33)
    party.addScenarioAvailable(40)
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 25)
    party.heroAdjustGold('JarJar', 28)
    party.heroAdjustCheckmarks('JarJar', 1)
    #party.heroAdjustXP('Bucky', 0)
    #party.heroAdjustGold('Bucky', 0)
    #party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustXP('Nova', 22)
    party.heroAdjustGold('Nova', 20)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Playgirl', 20)
    party.heroAdjustCheckmarks('Playgirl', 1)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 20)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustXP('Trog-dor', 26)
    party.heroAdjustGold('Trog-dor', 0)
    party.heroAdjustCheckmarks('Trog-dor', 1)
    #party.addGlobalAchievement('')
    #party.addPartyAchievement('')
    #party.addScenarioAvailable(0)
    #party.adjustReputation(0)
    party.heroLevelUp('Trog-dor', add_1_plus_2_muddle, 'Rocky End')


    # Play Session - August 12, 2019
    party.heroGainCheckmarkPerk('Drop', replace_0_with_plus_1_immobilize)
    party.heroLevelUp('Bucky', add_1_0_at, 'Eternal Equilibrium')
    
    party.completeCityEvent(25)
    party.heroAdjustGold('JarJar', -2)
    party.heroAdjustGold('Bucky', -3)
    party.heroAdjustGold('Playgirl', -2)
    party.heroAdjustGold('Drop', -3)

    party.completeRoadEvent(50)
    party.unlockCityEvent(68)

    #party.addTreasureLooted('', 0)
    party.addScenarioCompleted(94)
    party.addScenarioAvailable(95)
    party.addPartyAchievement('Through the Nest')
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 24)
    party.heroAdjustGold('JarJar', 36)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustGold('Bucky', 12)
    party.heroAdjustCheckmarks('Bucky', 0)
    #party.heroAdjustXP('Nova', 22)
    #party.heroAdjustGold('Nova', 20)
    #party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Playgirl', 16)
    party.heroAdjustCheckmarks('Playgirl', 2)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 20)
    party.heroAdjustCheckmarks('Drop', 1)
    #party.addGlobalAchievement('')
    #party.addScenarioAvailable(0)
    #party.adjustReputation(0)
    party.heroLevelUp('JarJar', add_2_roll_plus_1, 'Stiletto Storm')
    
    # Solo Scenario Attempt - Matt 
    party.heroAdjustXP('Nova', 22)
    party.heroLevelUp('Nova', add_2_roll_heal1, 'Cleansing Force')

    # Scenario - Aug 21 (Beach) with Stu
    hero19 = ch.Character('Cristal', 'spellweaver', owner_sm, level=1, gold=120, xp=345, quest=999)
    party.addMember(hero19)
    party.heroLevelUp('Cristal', remove_4_0, 'Icy Blast')
    party.heroLevelUp('Cristal', replace_minus_1_with_plus_1, 'Cold Fire')
    party.heroLevelUp('Cristal', replace_minus_1_with_plus_1, 'Spirit of Doom')
    party.heroLevelUp('Cristal', add_1_plus_1_wound, 'Chromatic Explosion')
    party.heroLevelUp('Cristal', add_1_plus_2_ice, 'Living Torch')
    party.heroLevelUp('Cristal', add_1_plus_2_ice, 'Twin Restoration')
    #party.heroBuyItem('Cristal', 'Boots of Dashing')
    #party.heroBuyItem('Cristal', 'Eagle-Eye Goggles')
    #party.heroBuyItem('Cristal', 'Piercing Bow')
    #party.heroBuyItem('Cristal', 'Minor Power Potion')
    #party.heroBuyItem('Cristal', 'Minor Stamina Potion')
    #party.heroBuyItem('Cristal', 'Moon Earring')
    party.heroBuyItem('JarJar', 'Volatile Bomb')
    
    party.completeCityEvent(58)
    party.addScenarioAvailable(91)
    party.completeRoadEvent(31)
    party.heroAdjustGold('Bucky', 5)
    party.heroAdjustGold('Drop', 5)
    party.heroAdjustGold('Cristal', 5)
    party.heroAdjustGold('JarJar', 5)
    party.heroAdjustGold('Nova', 5)
    #party.unlockCityEvent(68)

    party.addTreasureLooted(40, 'Drop')
    party.addItemDesign(73)
    party.addScenarioCompleted(87)
    #party.addScenarioAvailable(95)
    #party.addPartyAchievement('Through the Nest')
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 24)
    party.heroAdjustGold('JarJar', 8)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustGold('Bucky', 8)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustXP('Nova', 20)
    party.heroAdjustGold('Nova', 16)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustXP('Cristal', 29)
    party.heroAdjustGold('Cristal', 0)
    party.heroAdjustCheckmarks('Cristal', 0)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 16)
    party.heroAdjustCheckmarks('Drop', 0)
    #party.addGlobalAchievement('')
    #party.addScenarioAvailable(0)
    party.adjustReputation(1)
    party.addProsperityCheckmark('Scenario 87', 1)
    party.addEnhancement('Drop', 364, 'Bottom', 'Disarm', gold=375)
    
    # Solo Scenario Attempt - Matt 
    party.heroAdjustXP('Nova', 16)
    
    # Scenario - Aug 26
    party.completeCityEvent(34)
    #party.addScenarioAvailable(91)
    party.completeRoadEvent(34)
    #party.heroAdjustGold('Bucky', 5)
    #party.heroAdjustGold('Drop', 5)
    #party.heroAdjustGold('Cristal', 5)
    #party.heroAdjustGold('JarJar', 5)
    #party.heroAdjustGold('Nova', 5)
    #party.unlockCityEvent(68)

    party.addTreasureLooted(42, 'Bucky')
    party.addItemDesign(92)
    party.addScenarioCompleted(84)
    party.heroFindItem('Drop', 'Resonant Crystal')
    #party.addScenarioAvailable(95)
    #party.addPartyAchievement('Through the Nest')
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 22)
    party.heroAdjustGold('JarJar', 44)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustGold('Bucky', 12)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustXP('Nova', 22)
    party.heroAdjustGold('Nova', 20)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 28)
    party.heroAdjustCheckmarks('Drop', 1)
    #party.addGlobalAchievement('')
    #party.addScenarioAvailable(0)
    party.addProsperityCheckmark('Scenario 84', 1)
    #party.addEnhancement('Drop', 364, 'Bottom', 'Disarm', gold=375)

    party.unlockHero("Berserker")
    party.unlockCityEvent(36)
    party.unlockRoadEvent(36)
    party.unlockHero("Sawbones")
    party.unlockCityEvent(39)
    party.unlockRoadEvent(39)

    # Scenario - Sept 2
    party.heroBuyItem('Nova', "Steel Sabatons")
    party.heroGainCheckmarkPerk('Bucky', add_1_plus_1_wound)
    party.completeCityEvent(31)
    party.addScenarioAvailable(83)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustGold('Drop', 4)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustGold('JarJar', 4)
    party.heroAdjustGold('Nova', 4)
    party.addPartyAchievement("Bad Business")
    party.completeRoadEvent(39)
    party.heroAdjustGold('Bucky', -2)
    party.heroAdjustGold('Drop', -2)
    party.heroAdjustGold('Playgirl', -2)
    party.heroAdjustGold('JarJar', -2)
    party.heroAdjustGold('Nova', -2)
    #party.unlockCityEvent(68)

    #party.addTreasureLooted(42, 'Bucky')
    #party.addItemDesign(92)
    party.addScenarioCompleted(95)
    party.heroFindItem('Nova', 'Skull of Hatred')
    #party.heroFindItem('Drop', 'Resonant Crystal')
    #party.addScenarioAvailable(95)
    #party.addPartyAchievement('Through the Nest')
    #party.addProsperityCheckmark('', 0)
    party.heroAdjustXP('JarJar', 22)
    party.heroAdjustGold('JarJar', 0)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustXP('Nova', 22)
    party.heroAdjustGold('Nova', 4)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustXP('Drop', 0)
    party.heroAdjustGold('Drop', 8)
    party.heroAdjustCheckmarks('Drop', 1)
    party.heroAdjustXP('Playgirl', 0)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustCheckmarks('Playgirl', 0)
    #party.addGlobalAchievement('')
    #party.addScenarioAvailable(0)
    #party.addProsperityCheckmark('Scenario 84', 1)
    #party.addEnhancement('Drop', 364, 'Bottom', 'Disarm', gold=375)

    party.heroLevelUp('Nova', replace_minus_2_with_0, 'Divine Intervention')
    party.heroLevelUp('JarJar', add_2_roll_plus_1, 'Watch It Burn')
    party.retireHero(hero14)
    party.addEnhancement('Drop', 361, 'Bottom', 'Jump', gold=75)
    party.unlockCityEvent(54)
    party.unlockRoadEvent(54)
    
    hero20 = ch.Character('GH', 'berserker', owner_ag, level=1, gold=120, xp=345, quest=998)
    hero20.addOwnerPerk(remove_2_minus_1)
    hero20.addOwnerPerk(remove_4_0)
    hero20.addOwnerPerk(replace_minus_1_with_plus_1)
    hero20.addOwnerPerk(replace_minus_1_with_plus_1)
    party.addMember(hero20)
    party.heroLevelUp('GH', add_1_roll_stun, 'Break the Chains')
    party.heroLevelUp('GH', add_1_roll_stun, 'Fatal Fury')
    party.heroLevelUp('GH', replace_0_with_roll_plus_2, 'Flurry of Axes')
    party.heroLevelUp('GH', replace_0_with_roll_plus_2, 'Seeing Red')
    party.heroLevelUp('GH', add_1_roll_plus_1_disarm, 'Devil Horns')
    party.heroLevelUp('GH', add_1_plus_2_fire, 'Burning Hatred')
    party.heroBuyItem('GH', 'Cloak of Invisibility')
    party.heroBuyItem('GH', 'Battle-Axe')
    party.heroBuyItem('GH', 'Utility Belt')
    party.heroBuyItem('GH', 'Winged Shoes')
    party.heroBuyItem('GH', 'Major Stamina Potion')
    party.heroBuyItem('GH', 'Minor Power Potion')
    party.heroBuyItem('JarJar', 'Giant Remote Spider')

    # GH Solo Scenario
    party.heroAdjustXP('GH', 15)
    party.heroAdjustGold('GH', 12)
    party.heroFindItem('GH', 'Mask of Death')
    party.heroFindItem('Nova', 'Sun Shield')

    # Play Session - Sept 16
    party.retireHero(hero9)
    party.addEnhancement('Playgirl', 303, 'Top', '+1 Attack', gold=75)
    party.addEnhancement('Playgirl', 303, 'Top', '+1 Attack', gold=150)
    party.addEnhancement('Playgirl', 292, 'Bottom', '+1 Attack', gold=50)
    party.unlockCityEvent(52)
    party.unlockRoadEvent(52)
    hero21 = ch.Character('Bonesaw', 'Sawbones', owner_et, level=1, gold=120, xp=345, quest=997)
    hero21.addOwnerPerk(add_2_roll_wound)
    hero21.addOwnerPerk(add_2_roll_wound)
    party.addMember(hero21)
    party.heroLevelUp('Bonesaw', remove_2_minus_1, 'Hamstring')
    party.heroLevelUp('Bonesaw', remove_2_minus_1, 'Regenerative Tissue')
    party.heroLevelUp('Bonesaw', remove_4_0, 'Blood Transfusion')
    party.heroLevelUp('Bonesaw', add_1_roll_plus_2, 'Amputate')
    party.heroLevelUp('Bonesaw', add_1_roll_plus_2, 'Prescription')
    party.heroLevelUp('Bonesaw', add_1_roll_heal3, 'Master Physician')
    party.heroBuyItem('Bonesaw', 'Cloak of Invisibility')
    party.heroBuyItem('Bonesaw', 'Major Healing Potion')
    party.heroBuyItem('Bonesaw', 'Major Stamina Potion')
    party.heroBuyItem('Bonesaw', 'Eagle-Eye Goggles')
    party.heroBuyItem('Bonesaw', 'Minor Power Potion')

    party.completeCityEvent(54)
    party.heroAdjustGold('Bucky', 4)
    party.heroAdjustGold('JarJar', 4)
    party.heroAdjustGold('Bonesaw', 4)
    party.heroAdjustGold('GH', 4)
    party.heroAdjustGold('Nova', 4)
    party.heroBuyItem('Nova', 'Steel Ring')

    party.completeRoadEvent(36)

    party.addScenarioCompleted(34)
    party.addGlobalAchievement('The Drake Slain')
    #party.lossGlobalAchievement("The Drake's Command")
    party.adjustReputation(2)
    party.addProsperityCheckmark('Scenario 34', 1)

    party.heroAdjustGold('Bucky', 36)
    party.heroAdjustGold('GH', 20)
    party.heroAdjustGold('Bonesaw', 20)
    party.heroAdjustGold('JarJar', 32)
    party.heroAdjustGold('Nova', 24)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 34)
    party.heroAdjustXP('Bonesaw', 22)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('GH', 2)
    party.heroAdjustCheckmarks('Bonesaw', 0)

    party.unlockCityEvent(75)
    party.unlockRoadEvent(66)
    party.addScenarioAvailable(77) # from town record

    # Play Session - 23rd 
    party.heroBuyItem('JarJar', 'Hawk Helm')
    party.heroBuyItem('JarJar', 'Sacrificial Robes')
    party.heroBuyItem('JarJar', 'Major Power Potion')

    party.heroSellItem('Nova', 'Skull of Hatred')
    party.heroBuyItem('Nova', 'Spiked Shield')
    
    party.completeCityEvent(50)
    party.heroAdjustGold('Bucky', 10)
    party.heroAdjustGold('Bonesaw', 10)
    party.heroAdjustGold('JarJar', 10)
    party.heroAdjustGold('Nova', 10)

    party.heroBuyItem('Bucky', 'Minor Mana Potion')
    party.heroBuyItem('Nova', 'Ring of Haste')

    party.completeRoadEvent(66)
    party.heroAdjustGold('Bucky', 25)
    party.heroAdjustGold('Bonesaw', 25)
    party.heroAdjustGold('JarJar', 25)
    party.heroAdjustGold('Nova', 25)
    
    party.addTreasureLooted(64, 'JarJar')
    party.heroAdjustGold('JarJar', 30)
    #party.addItemDesign(92)
    
    party.addScenarioCompleted(48)
    party.addGlobalAchievement('End of Corruption')

    party.heroAdjustGold('Bucky', 0)
    #party.heroAdjustGold('GH', 20)
    party.heroAdjustGold('Bonesaw', 0)
    party.heroAdjustGold('JarJar', 24)
    party.heroAdjustGold('Nova', 24)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('GH', 34)
    party.heroAdjustXP('Bonesaw', 25)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Bucky', 1)
    party.heroAdjustCheckmarks('Nova', 0)
    #party.heroAdjustCheckmarks('GH', 2)
    party.heroAdjustCheckmarks('Bonesaw', 2)
    
    party.addScenarioAvailable(59) # retirement quest for Bucky 


    # Next Session - Sept 30, 2019
    party.heroGainCheckmarkPerk('JarJar', add_2_roll_muddle)
    party.heroBuyItem('JarJar', 'Sun Earring')
    party.heroGainCheckmarkPerk('Bucky', add_2_plus_1_push1)
    party.heroSellItem('Nova', 'Minor Stamina Potion')
    party.heroBuyItem('Nova', 'Major Stamina Potion')

    party.completeCityEvent(75) # super-imposed bad universal karma
    party.completeCityEvent(68)
    party.heroAdjustGold('JarJar', -6)
    party.heroAdjustGold('Nova', -3)
    party.heroAdjustGold('GH', -3)
    party.heroAdjustGold('Bucky', -3)
    party.addScenarioAvailable(88)
    party.addPartyAchievement('Water Staff')

    party.completeRoadEvent(54)
    party.adjustReputation(1)
    
    #party.addTreasureLooted(48, 'JarJar')
    #party.heroAdjustGold('JarJar', 30)
    #party.addItemDesign(92)
    
    party.addScenarioCompleted(59)

    party.heroAdjustGold('Bucky', 16)
    party.heroAdjustGold('GH', 4)
    party.heroAdjustGold('JarJar', 56)
    party.heroAdjustGold('Nova', 20)
    #party.heroAdjustGold('Bonesaw', 0)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 39)
    #party.heroAdjustXP('Bonesaw', 25)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('GH', 1)
    #party.heroAdjustCheckmarks('Bonesaw', 2)
    party.addScenarioAvailable(60)
    
    party.heroGainCheckmarkPerk('Nova', add_2_roll_plus_1)
    party.heroGainCheckmarkPerk('GH', add_1_plus_2_fire)
    party.heroLevelUp('GH', add_2_roll_wound, 'Bone Breaker')

    # Next Play Session - Oct 7, 2019
    party.makeSanctuaryDonation('Bucky')
    party.makeSanctuaryDonation('GH')
    party.heroSellItem('Bucky', 'Minor Mana Potion')
    party.heroBuyItem('Bucky', 'Minor Power Potion')

    party.completeCityEvent(52)
    party.adjustReputation(-2)

    party.completeRoadEvent(52)
    party.heroAdjustGold('Nova', 2)
    party.heroAdjustGold('Bonesaw', 3)
    party.heroAdjustGold('GH', 3)
    party.heroAdjustGold('Bucky', 2)
    
    #party.addTreasureLooted(48, 'JarJar')
    #party.heroAdjustGold('JarJar', 30)
    #party.addItemDesign(92)
    
    party.addScenarioCompleted(60)
    party.addProsperityCheckmark('Scenario 60')
    party.addGlobalAchievement('Finding the Cure')
    party.heroAdjustGold('Bucky', 0)
    party.heroAdjustGold('GH', 8)
    #party.heroAdjustGold('JarJar', 56)
    party.heroAdjustGold('Nova', 8)
    party.heroAdjustGold('Bonesaw', 4)
    #party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Bucky', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 43)
    party.heroAdjustXP('Bonesaw', 21)
    #party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Bonesaw', 2)
    party.heroAdjustCheckmarks('Bucky', 0)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('GH', 1)

    party.heroFindItem('Bucky', 'Drakescale Armor')
    party.retireHero(hero15)
    party.addEnhancement('Bucky', 475, 'Top', 'Add Wound', gold=350)
    party.addEnhancement('Bucky', 451, 'Bottom', '+1 Move', gold=30)
    party.addScenarioAvailable(67)
    party.addItemDesign(87)

    hero22 = ch.Character('Mer Sea', 'Doomstalker', owner_dp, level=1, gold=135, xp=420, quest=996)
    hero22.addOwnerPerk(remove_2_minus_1)
    hero22.addOwnerPerk(remove_2_minus_1)
    hero22.addOwnerPerk(replace_2_0_with_2_plus_1)
    hero22.addOwnerPerk(replace_2_0_with_2_plus_1)
    party.addMember(hero22)
    party.heroLevelUp('Mer Sea', replace_2_0_with_2_plus_1, 'Expose')
    party.heroLevelUp('Mer Sea', add_2_roll_plus_1, 'Darkened Skies')
    party.heroLevelUp('Mer Sea', add_2_roll_plus_1, 'Press the Attack')
    party.heroLevelUp('Mer Sea', add_1_plus_1_wound, 'Singular Focus')
    party.heroLevelUp('Mer Sea', add_1_roll_at, 'Inescapable Fate')
    party.heroLevelUp('Mer Sea', add_1_roll_at, 'Impending End')
    party.heroLevelUp('Mer Sea', ignore_scen_perk, 'Rising Momentum')
    party.heroBuyItem('Mer Sea', 'Telescopic Lens')
    party.heroBuyItem('Mer Sea', 'Minor Stamina Potion')
    party.heroBuyItem('Mer Sea', 'Moon Earring')
    party.heroBuyItem('Mer Sea', 'Robes of Evocation')
    party.heroBuyItem('Mer Sea', 'Wand of Infernos')
    party.heroSellItem('JarJar', 'Volatile Bomb')
    party.heroBuyItem('JarJar', 'Unstable Explosives')
    party.heroSellItem('JarJar', 'Sacrificial Robes')
    party.heroBuyItem('JarJar', 'Cloak of Phasing')
    party.heroSellItem('JarJar', 'Minor Power Potion')

    # Play Session Oct 28
    party.makeSanctuaryDonation('JarJar')
    party.completeCityEvent(39)
    party.unlockCityEvent(65)

    #party.completeRoadEvent(1)

    party.addScenarioCompleted(77)
    party.heroAdjustGold('Mer Sea', 16)
    party.heroAdjustGold('GH', 8)
    party.heroAdjustGold('JarJar', 36)
    #party.heroAdjustGold('Nova', 8)
    party.heroAdjustGold('Bonesaw', 16)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Mer Sea', 30)
    #party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 26)
    party.heroAdjustXP('Bonesaw', 28)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Bonesaw', 0)
    party.heroAdjustCheckmarks('Mer Sea', 0)
    #party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('GH', 1)

    # Play Session Nov 4, 2019
    party.heroLevelUp('GH', add_2_roll_wound, 'Immortality')
    party.heroLevelUp('Bonesaw', replace_0_with_plus_2, "Gentleman's Anger")
    party.heroGainCheckmarkPerk('Bonesaw', add_1_roll_heal3)
    party.heroSellItem('JarJar', 'Hawk Helm')
    party.heroBuyItem('JarJar', 'Telescopic Lens')
    party.heroBuyItem('JarJar', 'Doomed Compass')
    party.heroBuyItem('Nova', 'Sun Earring')

    party.completeCityEvent(36)
    party.adjustReputation(-2)
    party.heroAdjustXP('Bonesaw', 5)
    party.makeSanctuaryDonation('JarJar')

    #party.unlockCityEvent(65)

    #party.completeRoadEvent(8)
    party.addTreasureLooted(48, 'JarJar')
    party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(46)
    party.addGlobalAchievement('End of Corruption')
    #party.heroAdjustGold('Mer Sea', 16)
    party.heroAdjustGold('GH', 0)
    party.heroAdjustGold('JarJar', 12)
    party.heroAdjustGold('Nova', 4)
    party.heroAdjustGold('Bonesaw', 4)
    party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Mer Sea', 30)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 0)
    party.heroAdjustXP('Bonesaw', 18)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Bonesaw', 1)
    #party.heroAdjustCheckmarks('Mer Sea', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('GH', 0)


    # Play Session Nov 11, 2019
    party.completeCityEvent(65)
    party.adjustReputation(3)
    party.addProsperityCheckmark(1)
    party.makeSanctuaryDonation('JarJar')
    party.makeSanctuaryDonation('Bonesaw')
    party.makeSanctuaryDonation('GH')
    party.makeSanctuaryDonation('Mer Sea')

    #party.unlockCityEvent(65)

    #party.completeRoadEvent(68)
    party.adjustReputation(2)
    party.addTreasureLooted(56, 'JarJar')
    #party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(51)
    party.unlockCityEvent(81)
    party.unlockRoadEvent(69)
    party.addGlobalAchievement("End of Gloom")
    party.addProsperityCheckmark('Scenario 51', cnt=5)
    party.adjustReputation(5)
    party.heroSellItem('JarJar', 'Giant Remote Spider')

    party.heroAdjustGold('Mer Sea', 5)
    #party.heroAdjustGold('GH', 0)
    #party.heroAdjustGold('JarJar', 12)
    #party.heroAdjustGold('Nova', 4)
    #party.heroAdjustGold('Bonesaw', 4)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Mer Sea', 19)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 0)
    party.heroAdjustXP('Bonesaw', 22)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Bonesaw', 0)
    party.heroAdjustCheckmarks('Mer Sea', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('GH', 0)

    # Solo Doomstalker Scenarios
    party.heroAdjustXP('Mer Sea', 44)
    party.heroAdjustGold('Mer Sea', 24)
    party.heroLevelUp('Mer Sea', add_1_0_stun, 'Predator and Prey')
    party.heroBuyItem('Mer Sea', 'Ring of Haste')
    party.heroBuyItem('Mer Sea', 'Minor Power Potion')

    # Play Session Nov 25, 2019
    party.completeCityEvent(81)
    party.adjustReputation(2)
    #party.addProsperityCheckmark(1)
    #party.makeSanctuaryDonation('JarJar')

    party.unlockCityEvent(69)
    party.addProsperityCheckmark(1)
    party.heroAdjustCheckmarks('JarJar', -1)
    party.heroAdjustCheckmarks('Bonesaw', -1)
    party.heroAdjustCheckmarks('Mer Sea', -1)
    party.heroAdjustCheckmarks('Nova', -1)
    party.heroAdjustCheckmarks('GH', -1)

    #party.completeRoadEvent(68)
    #party.adjustReputation(2)
    party.addTreasureLooted(14, 'GH')
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(67)
    party.addGlobalAchievement("Ancient Technology")
    party.heroFindItem('Nova', "Power Core")

    party.heroAdjustGold('Mer Sea', 20)
    party.heroAdjustGold('GH', 4)
    party.heroAdjustGold('JarJar', 4)
    party.heroAdjustGold('Nova', 8)
    party.heroAdjustGold('Bonesaw', 0)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Mer Sea', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('GH', 0)
    party.heroAdjustXP('Bonesaw', 22)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Bonesaw', 1)
    party.heroAdjustCheckmarks('Mer Sea', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('GH', 0)


    # Play Session Dec 9, 2019
    party.completeCityEvent(69)
    party.adjustReputation(1)
    #party.makeSanctuaryDonation('JarJar')

    party.completeRoadEvent(69)
    party.heroAdjustCheckmarks('JarJar', -1)
    party.heroAdjustCheckmarks('Mer Sea', -1)
    party.heroAdjustCheckmarks('Nova', -1)
    party.heroAdjustCheckmarks('GH', -1)
    party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(14, 'GH')
    # Adjust XP by 10
    party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(83)
    #party.addGlobalAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")

    party.heroAdjustGold('Mer Sea', 50)
    party.heroAdjustGold('GH', 20)
    party.heroAdjustGold('JarJar', 10)
    party.heroAdjustGold('Nova', 20)
    #party.heroAdjustGold('Bonesaw', 0)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Mer Sea', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('GH', 0)
    #party.heroAdjustXP('Bonesaw', 22)
    #party.heroAdjustCheckmarks('JarJar', 0)
    #party.heroAdjustCheckmarks('Bonesaw', 1)
    #party.heroAdjustCheckmarks('Mer Sea', 0)
    #party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('GH', 0)


    # Play Session Dec 16, 2019
    #party.completeCityEvent(69)
    #party.adjustReputation(1)
    #party.makeSanctuaryDonation('JarJar')

    #party.completeRoadEvent(69)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.heroAdjustCheckmarks('Mer Sea', -1)
    #party.heroAdjustCheckmarks('Nova', -1)
    #party.heroAdjustCheckmarks('GH', -1)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(14, 'GH')
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(91)
    #party.addGlobalAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")

    #party.heroBuyItem('Trog-dor', 'Splintmail')
    party.heroAdjustGold('Trog-dor', 3)
    party.heroAdjustGold('Mer Sea', 27)
    #party.heroAdjustGold('GH', 20)
    party.heroAdjustGold('JarJar', 43)
    #party.heroAdjustGold('Nova', 20)
    party.heroAdjustGold('Bonesaw', 3)
    party.heroAdjustXP('Trog-dor', 16)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Mer Sea', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('GH', 0)
    #party.heroAdjustXP('Bonesaw', 22)
    party.heroAdjustCheckmarks('Trog-dor', 3)
    party.heroAdjustCheckmarks('JarJar', 2)
    party.heroAdjustCheckmarks('Bonesaw', 2)
    party.heroAdjustCheckmarks('Mer Sea', 2)
    #party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('GH', 0)

    party.heroBuyItem('Mer Sea', 'Unstable Explosives')
    party.heroBuyItem('Mer Sea', 'Ring of Brutality')

    # Play Session Jan 6, 2020
    #party.completeCityEvent(69)
    #party.adjustReputation(1)
    #party.makeSanctuaryDonation('JarJar')

    #party.completeRoadEvent(69)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.heroAdjustCheckmarks('Mer Sea', -1)
    #party.heroAdjustCheckmarks('Nova', -1)
    #party.heroAdjustCheckmarks('GH', -1)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(14, 'GH')
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(88)
    #party.addGlobalAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")

    #party.heroBuyItem('Trog-dor', 'Splintmail')
    #party.heroAdjustGold('Trog-dor', 3)
    #party.heroAdjustGold('Mer Sea', 27)
    #party.heroAdjustGold('GH', 20)
    party.heroAdjustGold('JarJar', 8)
    party.heroAdjustGold('Nova', 4)
    party.heroAdjustGold('Bonesaw', 24)
    #party.heroAdjustXP('Trog-dor', 16)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Mer Sea', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('GH', 0)
    #party.heroAdjustXP('Bonesaw', 22)
    #party.heroAdjustCheckmarks('Trog-dor', 3)
    party.heroAdjustCheckmarks('JarJar', 4)
    party.heroAdjustCheckmarks('Bonesaw', 1)
    #party.heroAdjustCheckmarks('Mer Sea', 2)
    party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('GH', 0)

    #party.heroBuyItem('Mer Sea', 'Unstable Explosives')
    #party.heroBuyItem('Mer Sea', 'Ring of Brutality')

    # Jan 13, 2020 - Session
    party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    party.heroAdjustGold('Nova', 30)
    #party.completeCityEvent(81)
    party.adjustReputation(2)
    party.makeSanctuaryDonation('JarJar')
    party.makeSanctuaryDonation('Mer Sea')
    party.makeSanctuaryDonation('GH')

    #party.completeRoadEvent(3)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.heroAdjustCheckmarks('Mer Sea', -1)
    #party.heroAdjustCheckmarks('Nova', -1)
    #party.heroAdjustCheckmarks('GH', -1)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(14, 'GH')
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')
    #party.heroAdjustGold('JarJar', 30)

    party.addScenarioCompleted(41)
    party.addProsperityCheckmark(2)
    #party.addGlobalAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")

    #party.heroBuyItem('Trog-dor', 'Splintmail')
    #party.heroAdjustGold('Trog-dor', 3)
    party.heroAdjustGold('Mer Sea', 54)
    party.heroAdjustGold('GH', 62)
    party.heroAdjustGold('JarJar', 86)
    party.heroAdjustGold('Nova', 66)
    #party.heroAdjustGold('Bonesaw', 24)
    #party.heroAdjustXP('Trog-dor', 16)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Mer Sea', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('GH', 0)
    #party.heroAdjustXP('Bonesaw', 22)
    #party.heroAdjustCheckmarks('Trog-dor', 3)
    party.heroAdjustCheckmarks('JarJar', 3)
    #party.heroAdjustCheckmarks('Bonesaw', 1)
    party.heroAdjustCheckmarks('Mer Sea', 2)
    party.heroAdjustCheckmarks('Nova', 2)
    party.heroAdjustCheckmarks('GH', 2)

    #party.heroBuyItem('Mer Sea', 'Unstable Explosives')
    #party.heroBuyItem('Mer Sea', 'Ring of Brutality')

    ##############################################################
    ##############################################################
    ## FORGOTTEN CIRCLES
    ##############################################################
    ##############################################################
    party.heroSellItem('Nova', "Power Core")
    party.unlockRoadEvent(82)
    party.unlockCityEvent(82)
    party.addScenarioAvailable(96)
    party.unlockHero("Diviner")
    party.retireHero(hero20)
    party.addEnhancement('GH', 336, "Bottom", 'Jump', gold=125)
    party.makeSanctuaryDonation('GH')

    hero23 = ch.Character('Loopy', 'diviner', owner_ag, level=1, gold=120, xp=345, quest=995)
    hero23.addOwnerPerk(ignore_scen_perk_2_plus_1)
    hero23.addOwnerPerk(replace_0_with_plus_1_shield1_ally)
    hero23.addOwnerPerk(replace_1_minus_1_with_1_plus_1_heal2_ally)
    hero23.addOwnerPerk(add_2_roll_heal1)
    hero23.addOwnerPerk(add_2_roll_curse)
    party.addMember(hero23)
    party.heroLevelUp('Loopy', replace_0_with_plus_2_regen, 'Gift of the Void')
    party.heroLevelUp('Loopy', remove_1_minus_2, 'Call of the Nether')
    party.heroLevelUp('Loopy', remove_2_minus_1, 'Preordain the Path')
    party.heroLevelUp('Loopy', remove_2_minus_1, 'Seal Their Fate')
    party.heroLevelUp('Loopy', replace_0_with_plus_2_dark, 'Enfeebling Hex')
    party.heroLevelUp('Loopy', replace_0_with_plus_2_light, 'Ethereal Vortex')
    party.heroBuyItem('Loopy', 'Cloak of Phasing')
    party.heroBuyItem('Loopy', 'Boots of Speed')
    party.heroBuyItem('Loopy', 'Major Stamina Potion')

    party.retireHero(hero22) # Danny - retires Doomstalker
    party.makeSanctuaryDonation('Mer Sea')
    party.retireHero(hero21) # Evan - retires Sawbones
    party.makeSanctuaryDonation('Bonesaw')
    party.retireHero(hero16) # Michael

    hero24 = ch.Character('Ashes', 'plagueherald', owner_dp, level=1, gold=120, xp=345, quest=994)
    hero24.addOwnerPerk(add_2_plus_1)
    hero24.addOwnerPerk(add_1_roll_stun)
    hero24.addOwnerPerk(add_1_roll_stun)
    hero24.addOwnerPerk(add_2_roll_curse)
    hero24.addOwnerPerk(add_3_roll_poison)
    party.addMember(hero24)
    party.heroLevelUp('Ashes', ignore_scen_perk_plus_1, 'Under the Skin')
    party.heroLevelUp('Ashes', replace_minus_2_with_0, 'Fetid Fury')
    party.heroLevelUp('Ashes', replace_minus_1_with_plus_1, 'Nightmarish Affliction')
    party.heroLevelUp('Ashes', replace_minus_1_with_plus_1, 'Accelerated End')
    party.heroLevelUp('Ashes', replace_0_with_plus_2, 'Black Tides')
    party.heroLevelUp('Ashes', replace_0_with_plus_2, 'Baneful Hex')
    party.heroBuyItem('Ashes', 'Star Earring')
    party.heroBuyItem('Ashes', 'Giant Remote Spider')

    hero25 = ch.Character('Rocky', 'cragheart', owner_et, level=1, gold=120, xp=345, quest=993)
    hero25.addOwnerPerk(ignore_scen_perk)
    hero25.addOwnerPerk(add_2_roll_push2)
    hero25.addOwnerPerk(remove_4_0)
    party.addMember(hero25)
    party.heroLevelUp('Rocky', replace_minus_1_with_plus_1, 'Explosive Punch')
    party.heroLevelUp('Rocky', replace_minus_1_with_plus_1, 'Clear the Way')
    party.heroLevelUp('Rocky', replace_minus_1_with_plus_1, 'Rock Slide')
    party.heroLevelUp('Rocky', add_2_roll_earth, 'Petrify')
    party.heroLevelUp('Rocky', add_2_roll_earth, 'Dig Pit')
    party.heroLevelUp('Rocky', add_1_plus_1_immobilize, 'Meteor')
    party.heroBuyItem('Rocky', 'Tower Shield')
    party.heroBuyItem('Rocky', 'Horned Helm')
    party.heroBuyItem('Rocky', 'Boots of Striding')
    party.heroBuyItem('Rocky', 'Minor Stamina Potion')
    party.heroBuyItem('Rocky', 'Tremor Blade')
    party.heroBuyItem('Rocky', 'Cloak of Invisibility')
    
    # July 9, 2020 - Session
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.heroAdjustGold('Nova', 30)
    party.completeCityEvent(82)
    party.makeSanctuaryDonation('JarJar')

    party.completeRoadEvent(82)
    # Rift Event
    party.unlockRiftEvent(1)
    party.completeRiftEvent(1)
    party.heroAdjustCheckmarks('JarJar', -1)
    party.heroAdjustCheckmarks('Ashes', -1)
    party.heroAdjustCheckmarks('Nova', -1)
    party.heroAdjustCheckmarks('Rocky', -1)
    party.heroAdjustCheckmarks('Loopy', -1)
    party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(91, 'Ashes')
    party.addPartyAchievement("Opportunist")
    party.heroAdjustGold('Ashes', 30)
    party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')

    party.addScenarioCompleted(96)
    #party.addProsperityCheckmark(2)
    party.addGlobalAchievement("Through the Portal")
    #party.addPartyAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(97)
    maxRiftID = 10
    party.unlockRiftEvent(2)
    party.unlockRiftEvent(3)
    party.unlockRiftEvent(4)
    party.unlockRiftEvent(5)
    party.unlockRiftEvent(6)
    party.unlockRiftEvent(7)
    party.unlockRiftEvent(8)
    party.unlockRiftEvent(9)
    party.unlockRiftEvent(10)

    party.heroAdjustGold('Ashes', 0)
    party.heroAdjustGold('Loopy', 0)
    party.heroAdjustGold('JarJar', 32)
    party.heroAdjustGold('Nova', 0)
    party.heroAdjustGold('Rocky', 0)
    party.heroAdjustXP('Ashes',45)
    party.heroAdjustXP('Loopy', 47)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 42)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 0)

    party.addEnhancement('Nova', 193, 'Bottom', 'Sun', gold=175)

    #party.heroBuyItem('Mer Sea', 'Unstable Explosives')
    #party.heroBuyItem('Mer Sea', 'Ring of Brutality')


    # July 16, 2020 - Session
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    party.makeSanctuaryDonation('JarJar')
    party.completeCityEvent(84)
    party.heroAdjustGold('Ashes', -30)
    party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    #party.unlockRiftEvent(1)
    party.completeRiftEvent(9)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.heroAdjustCheckmarks('Ashes', -1)
    #party.heroAdjustCheckmarks('Nova', -1)
    #party.heroAdjustCheckmarks('Rocky', -1)
    #party.heroAdjustCheckmarks('Loopy', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(91, 'Ashes')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')

    party.addScenarioCompleted(97)
    #party.addProsperityCheckmark(2)
    #party.addGlobalAchievement("Through the Portal")
    #party.addPartyAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(98)
    party.addScenarioAvailable(99)
    party.addScenarioAvailable(100)
    party.addScenarioAvailable(101)
    party.unlockCityEvent(88)
    party.unlockCityEvent(89)
    party.unlockCityEvent(90)
    #maxRiftID = 10

    party.heroAdjustGold('Ashes', 18)
    party.heroAdjustGold('Loopy', 14)
    party.heroAdjustGold('JarJar', 26)
    party.heroAdjustGold('Nova', 20)
    party.heroAdjustGold('Rocky', 18)
    party.heroAdjustXP('Ashes', 22)
    party.heroAdjustXP('Loopy', 25)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 22)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 0)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 0)
 
    # July 23, 2020 - Session
    party.heroGainCheckmarkPerk('JarJar', add_2_roll_pierce3)
    party.addEnhancement('JarJar', 90, 'Top', 'Strengthen', gold=0) # 
    party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    party.makeSanctuaryDonation('JarJar')
    party.heroBuyItem('Ashes', 'Minor Power Potion')
    party.heroBuyItem('Ashes', 'Minor Stamina Potion')
    party.heroBuyItem('Ashes', 'Iron Helmet')
    party.completeCityEvent(88)
    #party.heroAdjustGold('Ashes', -30)
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    #party.unlockRiftEvent(1)
    party.completeRiftEvent(5)
    # gain Elemental Claymore #156
    party.addItemDesign(156)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.heroAdjustCheckmarks('Ashes', -1)
    #party.heroAdjustCheckmarks('Nova', -1)
    #party.heroAdjustCheckmarks('Rocky', -1)
    #party.heroAdjustCheckmarks('Loopy', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(76, 'Nova')
    party.addTreasureLooted(85, 'JarJar')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('JarJar', 'Star Earring')

    party.addScenarioCompleted(100)
    #party.addProsperityCheckmark(2)
    party.addGlobalAchievement("Knowledge is Power")
    #party.addPartyAchievement("Ancient Technology")
    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(98)
    #party.addScenarioAvailable(99)
    #party.addScenarioAvailable(100)
    #party.addScenarioAvailable(101)
    #party.unlockCityEvent(88)
    #party.unlockCityEvent(89)
    #party.unlockCityEvent(90)
    #maxRiftID = 10

    party.heroAdjustGold('Ashes', 8)
    party.heroAdjustGold('Loopy', 8)
    party.heroAdjustGold('JarJar', 10)
    party.heroAdjustGold('Nova', 14)
    party.heroAdjustGold('Rocky', 0)
    party.heroAdjustXP('Ashes', 22)
    party.heroAdjustXP('Loopy', 26)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 16)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 0)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 0)

    party.heroFindItem('Ashes', 'Telescopic Lens')
    party.heroSellItem('Ashes', 'Iron Helmet')

    party.heroLevelUp('Ashes', add_2_roll_immobilize, 'Airborne Toxin')
    party.heroLevelUp('Loopy', replace_0_with_plus_3_muddle, 'Anguish and Salvation')
    party.heroLevelUp('Rocky', ignore_item_perk, 'Lumbering Bash')
    
    # Plagueherald solo 
    party.heroAdjustGold('Ashes', 20)
    party.heroAdjustXP('Ashes', 22)
    party.heroFindItem('Ashes', 'Pendant of the Plague')


    # July 30, 2020 - Session
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_pierce3)
    #party.addEnhancement('JarJar', 90, 'Top', 'Strengthen', gold=0) # 
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.makeSanctuaryDonation('JarJar')
    #party.heroBuyItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Minor Stamina Potion')
    #party.heroBuyItem('Ashes', 'Iron Helmet')
    party.completeCityEvent(90)
    #party.heroAdjustGold('Ashes', -30)
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    #party.unlockRiftEvent(1)
    #party.completeRiftEvent(4)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(76, 'Nova')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    party.heroFindItem('Loopy', 'Falcon Figurine')

    party.addScenarioCompleted(98)
    #party.addProsperityCheckmark(2)
    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(102)
    party.addScenarioAvailable(103)
    party.addPartyAchievement("Custodians")
    party.addGlobalAchievement("Knowledge is Power")
    party.unlockCityEvent(86)
    maxRiftID = 15
    party.unlockRiftEvent(11)
    party.unlockRiftEvent(12)
    party.unlockRiftEvent(13)
    party.unlockRiftEvent(14)
    party.unlockRiftEvent(15)

    party.heroAdjustGold('Ashes', 30)
    party.heroAdjustGold('Loopy', 10)
    party.heroAdjustGold('JarJar', 10)
    party.heroAdjustGold('Nova', 18)
    party.heroAdjustGold('Rocky', 18)
    party.heroAdjustXP('Ashes', 21)
    party.heroAdjustXP('Loopy', 23)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 18)
    party.heroAdjustCheckmarks('Ashes', 2)
    party.heroAdjustCheckmarks('Loopy', 0)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 0)

    party.heroGainCheckmarkPerk('Nova', add_2_roll_plus_1)
    party.heroSellItem('Ashes', 'Telescopic Lens')
    party.heroBuyItem('Ashes', 'Second Chance Ring')

    # Aug 6, 2020 - Session
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_pierce3)
    #party.addEnhancement('JarJar', 90, 'Top', 'Strengthen', gold=0) # 
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.makeSanctuaryDonation('JarJar')
    #party.heroBuyItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Minor Stamina Potion')
    #party.heroBuyItem('Ashes', 'Iron Helmet')
    party.completeCityEvent(86)
    party.heroFindItem('JarJar', 'Cutpurse Dagger')
    party.heroSellItem('JarJar', 'Heater Shield')
    #party.heroAdjustGold('Ashes', -30)
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    party.completeRiftEvent(11)
    party.heroAdjustXP('Ashes', 10)
    party.heroAdjustXP('Loopy', 10)
    party.heroAdjustXP('Rocky', 10)
    #party.completeRiftEvent(4)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(76, 'Nova')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('Loopy', 'Falcon Figurine')
    party.addTreasureLooted(95, 'JarJar')
    party.heroAdjustGold('JarJar', 25)
    party.unlockCityEvent(85)
    party.addPartyAchievement("A Strongbox")

    #party.addScenarioCompleted(99)
    #party.addProsperityCheckmark(2)
    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(102)
    #party.addScenarioAvailable(103)
    #party.addPartyAchievement("Custodians")
    #party.addGlobalAchievement("Knowledge is Power")
    #party.unlockCityEvent(86)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 28)
    party.heroAdjustGold('Loopy', 16)
    party.heroAdjustGold('JarJar', 44)
    party.heroAdjustGold('Nova', 0)
    party.heroAdjustGold('Rocky', 12)
    party.heroAdjustXP('Ashes', 8)
    party.heroAdjustXP('Loopy', 14)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 11)
    #party.heroAdjustCheckmarks('Ashes', 2)
    #party.heroAdjustCheckmarks('Loopy', 0)
    #party.heroAdjustCheckmarks('JarJar', 0)
    #party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('Rocky', 0)
    
    
    # Aug 13, 2020 - Session
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_pierce3)
    #party.addEnhancement('JarJar', 90, 'Top', 'Strengthen', gold=0) # 
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.makeSanctuaryDonation('JarJar')
    #party.heroBuyItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Minor Stamina Potion')
    #party.heroBuyItem('Ashes', 'Iron Helmet')
    party.completeCityEvent(85)
    party.heroAdjustCheckmarks('Ashes', -1)
    party.heroAdjustCheckmarks('Loopy', -1)
    party.heroAdjustCheckmarks('JarJar', -1)
    party.heroAdjustCheckmarks('Nova', -1)
    party.heroAdjustCheckmarks('Rocky', -1)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.heroAdjustGold('Ashes', -30)
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    party.completeRiftEvent(2)
    #party.heroAdjustXP('Ashes', 10)
    #party.heroAdjustXP('Loopy', 10)
    #party.heroAdjustXP('Rocky', 10)
    #party.completeRiftEvent(4)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(81, 'JarJar')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('Loopy', 'Falcon Figurine')
    #party.addTreasureLooted(95, 'JarJar')
    #party.heroAdjustGold('JarJar', 25)
    #party.addPartyAchievement("A Strongbox")

    party.addScenarioCompleted(103)
    party.heroFindItem('JarJar', 'Scroll of Haste')
    party.unlockCityEvent(87)
    party.addProsperityCheckmark(2)
    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(110)
    #party.addScenarioAvailable(103)
    party.addPartyAchievement("Guard Detail")
    #party.addGlobalAchievement("Knowledge is Power")
    #party.unlockCityEvent(86)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 36)
    party.heroAdjustGold('Loopy', 4)
    party.heroAdjustGold('JarJar', 50)
    party.heroAdjustGold('Nova', 16)
    party.heroAdjustGold('Rocky', 38)
    party.heroAdjustXP('Ashes', 26)
    party.heroAdjustXP('Loopy', 26)
    party.heroAdjustXP('JarJar', 0)
    party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 21)
    party.heroAdjustCheckmarks('Ashes', 1)
    party.heroAdjustCheckmarks('Loopy', 0)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 1)
    party.heroSellItem('JarJar', 'Scroll of Haste')

    party.heroLevelUp('Loopy', replace_0_with_plus_2_curse, 'Planar Fissure')
    party.heroBuyItem('Loopy', 'Telescopic Lens')
    party.heroBuyItem('Loopy', 'Minor Power Potion')
    party.heroLevelUp('Ashes', add_1_plus_1_air, 'Mass Extinction')
    #party.addEnhancement('JarJar', 104, 'Bottom', 'Bless', gold=125)

    # Aug 20, 2020 - Session
    party.makeSanctuaryDonation('JarJar')
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_pierce3)
    #party.addEnhancement('JarJar', 90, 'Top', 'Strengthen', gold=0) # 
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.makeSanctuaryDonation('JarJar')
    #party.heroBuyItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Minor Stamina Potion')
    #party.heroBuyItem('Ashes', 'Iron Helmet')
    party.completeCityEvent(87)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.heroAdjustGold('Ashes', -30)
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    party.completeRiftEvent(3)
    #party.heroAdjustXP('Ashes', 10)
    #party.heroAdjustXP('Loopy', 10)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(76, 'Nova')
    #party.addPartyAchievement("Opportunist")
    #party.heroAdjustGold('Ashes', 30)
    #party.unlockCityEvent(84)
    # Adjust XP by 10
    #party.heroFindItem('Loopy', 'Falcon Figurine')
    #party.addTreasureLooted(95, 'JarJar')
    #party.heroAdjustGold('JarJar', 25)
    #party.unlockCityEvent(85)
    #party.addPartyAchievement("A Strongbox")

    party.addScenarioCompleted(99)
    party.addProsperityCheckmark(1)
    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(104)
    party.addScenarioAvailable(105)
    #party.addPartyAchievement("Custodians")
    party.addGlobalAchievement("Knowledge is Power")
    party.addItemDesign(153)
    #party.unlockCityEvent(86)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 26)
    party.heroAdjustGold('Loopy', 22)
    party.heroAdjustGold('JarJar', 30)
    party.heroAdjustGold('Nova', 22)
    #party.heroAdjustGold('Rocky', 12)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 11)
    party.heroAdjustCheckmarks('Ashes', 1)
    party.heroAdjustCheckmarks('Loopy', 0)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('Rocky', 0)

    #party.heroSellItem('Loopy', 'Minor Power Potion')
    #party.heroBuyItem('Loopy', 'Major Power Potion')
    party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)


    # Aug 27, 2020 - Session
    party.makeSanctuaryDonation('JarJar')
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    party.heroBuyItem('Ashes', 'Staff of Elements')
    party.heroBuyItem('Rocky', 'Platemail')
    party.completeCityEvent(89)
    party.unlockCityEvent(89)
    party.heroAdjustGold('Ashes', -2)
    party.heroAdjustGold('Loopy', -2)
    party.heroAdjustGold('Rocky', -2)
    party.heroAdjustGold('JarJar', -2)
    party.heroAdjustGold('Nova', -2)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.adjustReputation(1)

    #party.completeRoadEvent(82)
    # Rift Event
    party.completeRiftEvent(6)
    party.completeRiftEvent(15)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(93, 'JarJar')
    party.heroFindItem('JarJar', 'Scroll of Haste')
    #party.heroAdjustGold('Ashes', 30)

    party.addScenarioCompleted(101)
    party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    party.addScenarioAvailable(108)
    party.addScenarioAvailable(109)
    #party.addPartyAchievement("Custodians")
    party.addGlobalAchievement("Knowledge is Power")
    #party.addItemDesign(153)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 44)
    party.heroAdjustGold('Loopy', 16)
    party.heroAdjustGold('JarJar', 28)
    party.heroAdjustGold('Nova', 16)
    party.heroAdjustGold('Rocky', 16)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 0)

    party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Loopy', 'Minor Power Potion')
    #party.heroBuyItem('Loopy', 'Major Power Potion')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)


    # Sept 3, 2020 - Session
    party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    party.heroSellItem('Loopy', 'Minor Power Potion')
    party.heroBuyItem('Loopy', 'Major Power Potion')
    party.heroBuyItem('Rocky', 'Major Healing Potion')
    party.heroBuyItem('Ashes', 'Cloak of Invisibility')

    #party.makeSanctuaryDonation('JarJar')
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.heroBuyItem('Ashes', 'Staff of Elements')
    #party.heroBuyItem('Rocky', 'Platemail')
    party.completeCityEvent(89)
    #party.unlockCityEvent(89)
    #party.heroAdjustGold('Ashes', -2)
    #party.heroAdjustGold('Loopy', -2)
    #party.heroAdjustGold('Rocky', -2)
    #party.heroAdjustGold('JarJar', -2)
    #party.heroAdjustGold('Nova', -2)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    party.completeRiftEvent(10)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(87, 'Loopy')
    #party.heroFindItem('JarJar', 'Scroll of Haste')
    #party.heroAdjustGold('Ashes', 30)

    party.addScenarioCompleted(104)
    party.addScenarioAvailable(111)

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    party.addPartyAchievement("Dimensional Equilibrium")
    #party.addGlobalAchievement("Knowledge is Power")
    #party.addItemDesign(153)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 4)
    party.heroAdjustGold('Loopy', 46)
    party.heroAdjustGold('JarJar', 16)
    party.heroAdjustGold('Nova', 0)
    party.heroAdjustGold('Rocky', 0)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 0)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Loopy', 'Minor Power Potion')
    #party.heroBuyItem('Loopy', 'Major Power Potion')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)

    # Sept 17, 2020 - Session
    #party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    party.heroSellItem('Ashes', 'Minor Power Potion')
    party.heroBuyItem('Ashes', 'Major Power Potion')
    #party.heroBuyItem('Rocky', 'Major Healing Potion')
    #party.heroBuyItem('Ashes', 'Cloak of Invisibility')

    #party.makeSanctuaryDonation('JarJar')
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.heroBuyItem('Ashes', 'Staff of Elements')
    #party.heroBuyItem('Rocky', 'Platemail')
    #party.completeCityEvent(13)
    #party.unlockCityEvent(89)
    party.heroAdjustGold('Ashes', -3)
    party.heroAdjustGold('Loopy', -3)
    #party.heroAdjustGold('Rocky', -2)
    party.heroAdjustGold('JarJar', -3)
    party.heroAdjustGold('Nova', -3)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    party.completeRiftEvent(12)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(87, 'Loopy')
    party.heroFindItem('JarJar', 'Mask of Terror')
    party.heroSellItem('JarJar', 'Mask of Terror')
    #party.heroAdjustGold('Ashes', 30)

    party.addScenarioCompleted(110)
    #party.addScenarioAvailable(111)
    party.heroFindItem("Ashes", "Crystal Tiara")
    party.heroSellItem("Ashes", "Crystal Tiara")

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    #party.addPartyAchievement("Dimensional Equilibrium")
    party.addGlobalAchievement("A Peril Averted")
    #party.addItemDesign(153)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 8)
    party.heroAdjustGold('Loopy', 0)
    party.heroAdjustGold('JarJar', 4)
    party.heroAdjustGold('Nova', 0)
    #party.heroAdjustGold('Rocky', 0)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 1)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 0)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Loopy', 'Minor Power Potion')
    #party.heroBuyItem('Loopy', 'Major Power Potion')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)


    # Challenge - Black Tower
    ##############################
    #party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    #party.heroSellItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Major Power Potion')
    #party.heroBuyItem('Rocky', 'Major Healing Potion')
    #party.heroBuyItem('Ashes', 'Cloak of Invisibility')

    #party.makeSanctuaryDonation('JarJar')
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.heroBuyItem('Ashes', 'Staff of Elements')
    #party.heroBuyItem('Rocky', 'Platemail')
    #party.completeCityEvent(13)
    #party.unlockCityEvent(89)
    #party.heroAdjustGold('Ashes', -3)
    #party.heroAdjustGold('Loopy', -3)
    #party.heroAdjustGold('Rocky', -2)
    #party.heroAdjustGold('JarJar', -3)
    #party.heroAdjustGold('Nova', -3)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    #party.completeRiftEvent(12)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(87, 'Loopy')
    #party.heroFindItem('JarJar', 'Mask of Terror')
    #party.heroSellItem('JarJar', 'Mask of Terror')
    #party.heroAdjustGold('Ashes', 30)

    #party.addScenarioCompleted(110)
    #party.addScenarioAvailable(111)
    party.heroFindItem("Rocky", "Second Chance Ring")
    #party.heroSellItem("Ashes", "Crystal Tiara")

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    party.addPartyAchievement("Beauty in Freedom")
    #party.addGlobalAchievement("A Peril Averted")
    #party.addItemDesign(153)
    #maxRiftID = 15

    party.heroAdjustGold('Ashes', 35)
    #party.heroAdjustGold('Loopy', 0)
    party.heroAdjustGold('JarJar', 63)
    party.heroAdjustGold('Nova', 31)
    party.heroAdjustGold('Rocky', 27)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 0)
    #party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 2)
    party.heroAdjustCheckmarks('Rocky', 2)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    party.heroSellItem('Nova', 'Spiked Shield')
    party.heroBuyItem('Nova', 'Balanced Blade')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)
    
    # Oct 8, 2020
    party.heroGainCheckmarkPerk('Nova', replace_0_with_plus_2)
    party.addEnhancement('Nova', 183, 'Bottom', 'Sun', gold=100)
    party.heroGainCheckmarkPerk('Rocky', add_1_plus_2_muddle)
    #party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    #party.heroSellItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Major Power Potion')
    #party.heroBuyItem('Rocky', 'Major Healing Potion')
    #party.heroBuyItem('Ashes', 'Cloak of Invisibility')

    #party.makeSanctuaryDonation('JarJar')
    #party.addEnhancement('JarJar', 109, 'Top', 'Attack +Dark', gold=225)
    #party.heroGainCheckmarkPerk('JarJar', add_2_roll_poison)
    #party.heroSellItem('Nova', 'Staff of Summoning')
    #party.heroBuyItem('Ashes', 'Staff of Elements')
    #party.heroBuyItem('Rocky', 'Platemail')
    #party.completeCityEvent(71)
    party.unlockCityEvent(72)

    #party.heroAdjustGold('Ashes', -3)
    #party.heroAdjustGold('Loopy', -3)
    #party.heroAdjustGold('Rocky', -2)
    #party.heroAdjustGold('JarJar', -3)
    #party.heroAdjustGold('Nova', -3)
    #party.heroFindItem('JarJar', 'Cutpurse Dagger')
    #party.heroSellItem('JarJar', 'Heater Shield')
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    party.completeRiftEvent(4)
    #party.heroAdjustXP('Rocky', 10)
    # gain Elemental Claymore #156
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addEnhancement('JarJar', 97, 'Bottom', '+1 Move', gold=0)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    #party.addTreasureLooted(87, 'Loopy')
    #party.heroFindItem('JarJar', 'Mask of Terror')
    #party.heroSellItem('JarJar', 'Mask of Terror')
    #party.heroAdjustGold('Ashes', 30)

    party.addScenarioCompleted(102)
    party.adjustReputation(-2)
    party.heroAdjustGold('Rocky', -5)
    #party.addScenarioAvailable(111)
    party.heroFindItem("Loopy", "Major Cure Potion")
    # PARTY - UNLOCK SOLO SCENARIO FOR DIVINER
    #party.heroSellItem("Ashes", "Crystal Tiara")

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    #party.addPartyAchievement("Beauty in Freedom")
    #party.addGlobalAchievement("A Peril Averted")
    #party.addItemDesign(153)
    #maxRiftID = 15

    #party.heroAdjustGold('Ashes', 35)
    #party.heroAdjustGold('Loopy', 0)
    #party.heroAdjustGold('JarJar', 63)
    #party.heroAdjustGold('Nova', 31)
    #party.heroAdjustGold('Rocky', 27)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 2)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Nova', 'Spiked Shield')
    #party.heroBuyItem('Nova', 'Balanced Blade')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)
    
    # Oct 15, 2020
    party.heroGainCheckmarkPerk('Loopy', replace_2_plus_1_with_1_plus_3_shield1)
    party.addEnhancement('JarJar', 110, 'Bottom', 'Bless', gold=200)
    #party.addEnhancement('Nova', 183, 'Bottom', 'Sun', gold=100)
    #party.heroGainCheckmarkPerk('Rocky', add_1_plus_2_muddle)
    #party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    #party.heroSellItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Major Power Potion')

    party.completeCityEvent(72)
    party.addPartyAchievement("Fish's Aid")
    party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    party.completeRiftEvent(14)
    party.addPartyAchievement("Saboteurs")
    party.heroAdjustGold('Rocky', 5)
    party.heroAdjustGold('Loopy', 5)
    party.heroAdjustGold('JarJar', 5)
    party.heroAdjustGold('Ashes', 5)
    #party.heroAdjustXP('Rocky', 10)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(83, 'JarJar')
    party.heroFindItem('JarJar', 'Major Power Potion')
    party.heroSellItem('JarJar', 'Major Power Potion')
    party.addTreasureLooted(88, 'Loopy')
    party.heroAdjustCheckmarks('Loopy', 1)

    party.addScenarioCompleted(105)
    #party.adjustReputation(-2)
    #party.heroAdjustGold('Rocky', -5)
    #party.addScenarioAvailable(111)
    party.addItemDesign(154)
    #party.heroFindItem("Loopy", "Major Cure Potion")
    #party.heroSellItem("Ashes", "Crystal Tiara")

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    #party.addPartyAchievement("Beauty in Freedom")
    #party.addGlobalAchievement("A Peril Averted")
    #party.addItemDesign(153)

    party.heroAdjustGold('Ashes', 16)
    party.heroAdjustGold('Loopy', 4)
    party.heroAdjustGold('JarJar', 36)
    #party.heroAdjustGold('Nova', 31)
    party.heroAdjustGold('Rocky', 8)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 0)
    #party.heroAdjustCheckmarks('Nova', 0)
    party.heroAdjustCheckmarks('Rocky', 0)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Nova', 'Spiked Shield')
    #party.heroBuyItem('Nova', 'Balanced Blade')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)


    # Nov 12, 2020
    #party.heroGainCheckmarkPerk('Loopy', replace_2_plus_1_with_1_plus_3_shield1)
    #party.addEnhancement('JarJar', 110, 'Bottom', 'Bless', gold=200)
    #party.addEnhancement('Nova', 183, 'Bottom', 'Sun', gold=100)
    #party.heroGainCheckmarkPerk('Rocky', add_1_plus_2_muddle)
    #party.heroLevelUp('Rocky', add_1_plus_2_muddle, 'Blind Destruction')
    #party.heroSellItem('Ashes', 'Minor Power Potion')
    #party.heroBuyItem('Ashes', 'Major Power Potion')

    #party.completeCityEvent(99)
    #party.addPartyAchievement("Fish's Aid")
    #party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)

    # Rift Event
    party.completeRiftEvent(8)
    #party.addPartyAchievement("Saboteurs")
    #party.heroAdjustGold('Rocky', 5)
    #party.heroAdjustGold('Loopy', 5)
    #party.heroAdjustGold('JarJar', 5)
    #party.heroAdjustGold('Ashes', 5)
    #party.heroAdjustXP('Rocky', 10)
    #party.heroAdjustCheckmarks('JarJar', -1)
    #party.addProsperityCheckmark(1)
    #party.adjustReputation(2)
    party.addTreasureLooted(94, 'JarJar')
    party.unlockRiftEvent(20)
    #party.heroFindItem('JarJar', 'Major Power Potion')
    #party.heroSellItem('JarJar', 'Major Power Potion')
    #party.addTreasureLooted(88, 'Loopy')
    #party.heroAdjustCheckmarks('Loopy', 1)

    party.addScenarioCompleted(109)
    #party.adjustReputation(-2)
    #party.heroAdjustGold('Rocky', -5)
    party.addScenarioAvailable(113)
    #party.addItemDesign(154)
    party.heroFindItem("Loopy", "Protective Charm")
    #party.heroSellItem("Ashes", "Crystal Tiara")

    #party.addProsperityCheckmark(1)

    #party.heroFindItem('Nova', "Power Core")
    #party.addScenarioAvailable(108)
    #party.addScenarioAvailable(109)
    #party.addPartyAchievement("Beauty in Freedom")
    #party.addGlobalAchievement("A Peril Averted")
    #party.addItemDesign(153)

    party.heroAdjustGold('Ashes', 4)
    #party.heroAdjustGold('Loopy', 4)
    party.heroAdjustGold('JarJar', 8)
    #party.heroAdjustGold('Nova', 31)
    #party.heroAdjustGold('Rocky', 8)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    #party.heroAdjustCheckmarks('Ashes', 0)
    party.heroAdjustCheckmarks('Loopy', 1)
    #party.heroAdjustCheckmarks('JarJar', 0)
    #party.heroAdjustCheckmarks('Nova', 0)
    #party.heroAdjustCheckmarks('Rocky', 0)

    #party.heroSellItem('JarJar', 'Scroll of Haste')
    #party.heroSellItem('Nova', 'Spiked Shield')
    #party.heroBuyItem('Nova', 'Balanced Blade')
    #party.heroGainCheckmarkPerk('Nova', add_1_roll_stun)
    #party.heroGainCheckmarkPerk('Ashes', add_1_plus_1_air)

    
    # May 6, 2021
    #party.completeCityEvent(18)
    party.heroAdjustGold('Ashes', 2)
    party.heroAdjustGold('Loopy', 2)
    party.heroAdjustGold('JarJar', 2)
    party.heroAdjustGold('Rocky', 2)
    #party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)

    #party.completeRoadEvent(89)
    party.addScenarioCompleted(111)
    party.addPartyAchievement("Hunted Party")
    party.unlockRiftEvent(16)
    party.addItemDesign(158)

    party.heroAdjustGold('Ashes', 8)
    party.heroAdjustGold('Loopy', 0)
    party.heroAdjustGold('JarJar', 8)
    #party.heroAdjustGold('Nova', 31)
    party.heroAdjustGold('Rocky', 12)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    #party.heroAdjustCheckmarks('Ashes', 0)
    #party.heroAdjustCheckmarks('Loopy', 1)
    #party.heroAdjustCheckmarks('JarJar', 0)
    #party.heroAdjustCheckmarks('Nova', 0)
    #party.heroAdjustCheckmarks('Rocky', 0)

    # June 10, 2021
    party.heroBuyItem('Ashes', 'Rejuvenation Greaves')
    party.makeSanctuaryDonation('JarJar')
    party.makeSanctuaryDonation('Nova')
    party.makeSanctuaryDonation('Rocky')
    party.heroAdjustGold('Ashes', -3)
    party.heroAdjustGold('Loopy', -3)
    party.heroAdjustGold('JarJar', -3)
    party.heroAdjustGold('Nova', -1)
    party.heroAdjustGold('Rocky', -3)
    #party.completeCityEvent(18)
    #party.heroAdjustGold('Ashes', 2)
    #party.heroAdjustGold('Loopy', 2)
    #party.heroAdjustGold('JarJar', 2)
    #party.heroAdjustGold('Rocky', 2)
    #party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)


    #party.completeRoadEvent(89)
    #party.addScenarioCompleted(111)
    #party.addPartyAchievement("Hunting the Hunter")
    party.addGlobalAchievement("A Peril Averted")
    #party.unlockRiftEvent(16)
    #party.addItemDesign(158)

    party.heroAdjustGold('Ashes', 16)
    party.heroAdjustGold('Loopy', 0)
    party.heroAdjustGold('JarJar', 12)
    party.heroAdjustGold('Nova', 0)
    party.heroAdjustGold('Rocky', 0)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    party.heroAdjustCheckmarks('Ashes', 1)
    party.heroAdjustCheckmarks('Loopy', 1)
    party.heroAdjustCheckmarks('JarJar', 1)
    party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 3)
    party.addScenarioAvailable(114)

    party.heroBuyItem("Rocky", "Rejuvenation Greaves")
    
    # June 24, 2021
    party.heroGainCheckmarkPerk('Rocky', [add_1_minus_2, add_2_plus_2])
    party.heroAdjustGold('Ashes', -5)
    party.heroAdjustGold('Loopy', -5)
    party.heroAdjustGold('JarJar', -5)
    party.heroAdjustGold('Nova', -5)
    party.heroAdjustGold('Rocky', -5)
    #party.heroBuyItem('Ashes', 'Rejuvenation Greaves')
    #party.makeSanctuaryDonation('JarJar')
    #party.makeSanctuaryDonation('Nova')
    #party.makeSanctuaryDonation('Rocky')
    #party.heroAdjustGold('Ashes', -3)
    #party.heroAdjustGold('Loopy', -3)
    #party.heroAdjustGold('JarJar', -3)
    #party.heroAdjustGold('Nova', -1)
    #party.heroAdjustGold('Rocky', -3)
    #party.completeCityEvent(18)
    #party.heroAdjustGold('Ashes', 2)
    #party.heroAdjustGold('Loopy', 2)
    #party.heroAdjustGold('JarJar', 2)
    #party.heroAdjustGold('Rocky', 2)
    #party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)


    #party.completeRoadEvent(89)
    party.addScenarioCompleted(114)
    party.addScenarioAvailable(115)
    party.addPartyAchievement("Party Boon")
    #party.addGlobalAchievement("A Peril Averted")
    #party.unlockRiftEvent(16)
    #party.addItemDesign(158)

    party.heroAdjustGold('Ashes', 8)
    party.heroAdjustGold('Loopy', 16)
    party.heroAdjustGold('JarJar', 24)
    party.heroAdjustGold('Nova', 4)
    party.heroAdjustGold('Rocky', 8)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    #party.heroAdjustCheckmarks('Ashes', 1)
    #party.heroAdjustCheckmarks('Loopy', 1)
    #party.heroAdjustCheckmarks('JarJar', 1)
    #party.heroAdjustCheckmarks('Nova', 1)
    party.heroAdjustCheckmarks('Rocky', 1)

    # Sept 16, 2021
    #party.heroGainCheckmarkPerk('Rocky', [add_1_minus_2, add_2_plus_2])
    #party.heroAdjustGold('Ashes', -5)
    #party.heroAdjustGold('Loopy', -5)
    #party.heroAdjustGold('JarJar', -5)
    #party.heroAdjustGold('Nova', -5)
    #party.heroAdjustGold('Rocky', -5)
    #party.heroBuyItem('Ashes', 'Rejuvenation Greaves')
    party.makeSanctuaryDonation('JarJar')
    #party.makeSanctuaryDonation('Nova')
    party.makeSanctuaryDonation('Rocky')
    #party.heroAdjustGold('Ashes', -3)
    #party.heroAdjustGold('Loopy', -3)
    #party.heroAdjustGold('JarJar', -3)
    #party.heroAdjustGold('Nova', -1)
    #party.heroAdjustGold('Rocky', -3)
    #party.completeCityEvent(18)
    #party.heroAdjustGold('Ashes', 2)
    #party.heroAdjustGold('Loopy', 2)
    #party.heroAdjustGold('JarJar', 2)
    #party.heroAdjustGold('Rocky', 2)
    #party.addScenarioAvailable(79)
    #party.unlockCityEvent(72)
    #party.adjustReputation(1)


    party.completeRiftEvent(13)
    party.addGlobalAchievement('Ancient Technology')
    party.heroFindItem('Loopy', 'Ancient Bow')

    #party.addScenarioCompleted(115)
    #party.addPartyAchievement("Party Boon")
    #party.addGlobalAchievement("A Peril Averted")
    #party.unlockRiftEvent(16)
    #party.addItemDesign(158)

    #party.heroAdjustGold('Ashes', 8)
    #party.heroAdjustGold('Loopy', 16)
    #party.heroAdjustGold('JarJar', 24)
    #party.heroAdjustGold('Nova', 4)
    #party.heroAdjustGold('Rocky', 8)
    #party.heroAdjustXP('Ashes', 8)
    #party.heroAdjustXP('Loopy', 14)
    #party.heroAdjustXP('JarJar', 0)
    #party.heroAdjustXP('Nova', 0)
    #party.heroAdjustXP('Rocky', 19)
    #party.heroAdjustCheckmarks('Ashes', 1)
    #party.heroAdjustCheckmarks('Loopy', 1)
    #party.heroAdjustCheckmarks('JarJar', 1)
    #party.heroAdjustCheckmarks('Nova', 1)
    #party.heroAdjustCheckmarks('Rocky', 1)

    # Sept 24, 2021
    party.heroAdjustGold('Ashes', 24)
    party.addEnhancement('Ashes', 312, 'Top', '+1 Attack', gold=145)
    party.addEnhancement('Ashes', 292, 'Bottom', '+1 Range', gold=0)
    party.addEnhancement('Loopy', 599, 'Top', '+1 Range', gold=55)
    party.heroAdjustGold('JarJar', 135)
    party.addEnhancement('JarJar', 109, 'Top', '+1 Range', gold=200)
    party.addEnhancement('JarJar', 104, 'Bottom', '+1 Move', gold=85)
    party.addScenarioCompleted(113)
    party.completeRiftEvent(7)
    party.addProsperityCheckmark(1)
    party.addGlobalAchievement("A Peril Averted")
    party.heroFindItem('JarJar', 'Magma Waders')

    # Stuff
    party.heroSellItem('Rocky', 'Cloak of Invisibility')
    party.heroSellItem('Rocky', 'Boots of Striding')
    party.heroSellItem('JarJar', 'Telescopic Lens')
    party.heroSellItem('JarJar', 'Doomed Compass')
    party.addEnhancement('JarJar', 92, 'Bottom', 'Dark', gold=100)
    party.heroSellItem('Loopy', 'Protective Charm')
    party.heroAdjustGold('JarJar', 20)
    party.heroAdjustGold('JarJar', 24)
    party.heroAdjustGold('Loopy', 4)

    hero26 = ch.Character('PoonStalker', 'doomstalker', owner_et, level=1, gold=150, xp=345, quest=992)
    #hero26.addOwnerPerk(ignore_scen_perk)
    #hero26.addOwnerPerk(add_2_roll_push2)
    #hero26.addOwnerPerk(remove_4_0)
    party.addMember(hero26)
    #party.heroLevelUp('PoonStalker', replace_minus_1_with_plus_1, 'Explosive Punch')
    #party.heroLevelUp('PoonStalker', replace_minus_1_with_plus_1, 'Clear the Way')
    #party.heroLevelUp('PoonStalker', replace_minus_1_with_plus_1, 'Rock Slide')
    #party.heroLevelUp('PoonStalker', add_2_roll_earth, 'Petrify')
    #party.heroLevelUp('PoonStalker', add_2_roll_earth, 'Dig Pit')
    #party.heroLevelUp('PoonStalker', add_1_plus_1_immobilize, 'Meteor')
    #party.heroLevelUp('PoonStalker', add_1_plus_1_immobilize, 'Meteor')
    #party.heroLevelUp('PoonStalker', add_1_plus_1_immobilize, 'Meteor')
    #party.heroBuyItem('PoonStalker', 'Tower Shield')
    #party.heroBuyItem('PoonStalker', 'Horned Helm')
    #party.heroBuyItem('PoonStalker', 'Boots of Striding')
    #party.heroBuyItem('PoonStalker', 'Minor Stamina Potion')
    hero27 = ch.Character('BabyBackBitch', 'berserker', owner_dp, level=1, gold=150, xp=345, quest=991)
    #hero27.addOwnerPerk(ignore_scen_perk)
    #hero27.addOwnerPerk(add_2_roll_push2)
    #hero27.addOwnerPerk(remove_4_0)
    party.addMember(hero27)
    #party.heroLevelUp('BabyBackBitch', replace_minus_1_with_plus_1, 'Explosive Punch')
    #party.heroLevelUp('BabyBackBitch', replace_minus_1_with_plus_1, 'Clear the Way')
    #party.heroLevelUp('BabyBackBitch', replace_minus_1_with_plus_1, 'Rock Slide')
    #party.heroLevelUp('BabyBackBitch', add_2_roll_earth, 'Petrify')
    #party.heroLevelUp('BabyBackBitch', add_2_roll_earth, 'Dig Pit')
    #party.heroLevelUp('BabyBackBitch', add_1_plus_1_immobilize, 'Meteor')
    #party.heroLevelUp('BabyBackBitch', add_1_plus_1_immobilize, 'Meteor')
    #party.heroLevelUp('BabyBackBitch', add_1_plus_1_immobilize, 'Meteor')
    #party.heroBuyItem('BabyBackBitch', 'Tower Shield')
    #party.heroBuyItem('BabyBackBitch', 'Horned Helm')
    #party.heroBuyItem('BabyBackBitch', 'Boots of Striding')
    #party.heroBuyItem('BabyBackBitch', 'Minor Stamina Potion')

    party.heroAdjustGold('PoonStalker', 8)
    party.heroAdjustGold('BabyBackBitch', 12)
    party.heroFindItem('BabyBackBitch', 'Helix Ring')
    party.addScenarioAvailable(81)
    party.addScenarioCompleted(81)

    ##############################################
    # Next Play Session
    try:
        randScenario = party.drawRandomScenario()
        print("Randomed Scenario Event: %d" % randScenario)
    except:
        print("No More Scenarios Left")
        pass

    cityEvent = party.drawRandomCityEvent()
    print("Randomed City Event: %d" % cityEvent)
    roadEvent = party.drawRandomRoadEvent()
    print("Randomed Road Event: %d" % roadEvent)
    riftEvent = party.drawRandomRiftEvent(maxRiftID)
    print("Randomed Rift Event: %d" % riftEvent)

    ###
    #  PRINT OUR PARTY
    ###
    #printJson(party)

    suggestedScenLevel = party.calcAvgLevel()
    print("Current Normal Difficulty Level: %d, For Parties of 5: %d\n" % (suggestedScenLevel, suggestedScenLevel+2))
    print("Trap Damage 2-4: %d, 5: %d" % (calculateTrapDamage(suggestedScenLevel), calculateTrapDamage(suggestedScenLevel+2)))
    print("Hazard Damage 2-4: %d, 5: %d" % (calculateHazardDamage(suggestedScenLevel), calculateHazardDamage(suggestedScenLevel+2)))
    print("Gold Conversion 2-5: %d" % (calculateGoldConversion(suggestedScenLevel)))
    print("Bonus XP on Success 2-5: %d" % (calculateBonusExperience(suggestedScenLevel)))
    party.saveParty()

    return party

if __name__ == "__main__":
    party = make_a_party()
    party.loadParty('TheBrotherhood')
    #printJson(party)
