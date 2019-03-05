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
        except AssertionError as err:
            print('[completeCityEvent:: AssertionError] %s' % (err))
            raise

    def unlockCityEvent(self, value):
        try:
            assert value not in self.party_json['UnlockedCityEvents']
            self.party_json['UnlockedCityEvents'].append(value)
        except AssertionError as err:
            print('[unlockCityEvent :: AssertionError] %s' % (err))
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
            pool.remove(done)
        drawn = pickRandom(pool)
        #self.completeCityEvent(drawn)
        return drawn

    def drawRandomRoadEvent(self, maxID=30):
        pool = [i for i in range(1,maxID+1)] # +1 to make it inclusive
        for unlocked in self.party_json['UnlockedRoadEvents']:
            pool.append(unlocked)
        for done in self.party_json['CompletedRoadEvents']:
            pool.remove(done)
        drawn = pickRandom(pool)
        #self.completeRoadEvent(drawn)
        return drawn

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
        count_req = [sum(count_per_increment[:i]) for i in range(1,9)]
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

    owner1 = ch.Owner('Andrzej')
    owner2 = ch.Owner('Danny')
    owner3 = ch.Owner('Evan')
    owner4 = ch.Owner('Matt')
    owner5 = ch.Owner('Kyle')

    hero1 = ch.Character('Clockwerk', 'Tinkerer', owner1, level=5, xp=225, gold=24, quest=528, checkmarks=10)
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

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', owner2, level=3, quest=512, gold=191, xp=161, checkmarks=5)
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

    hero3 = ch.Character('Evan', 'Spellweaver', owner3, level=4, quest=533, gold=39, xp=208, checkmarks=9)
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

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', owner4, level=4, quest=531, gold=32, xp=203, checkmarks=8)
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

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', owner5, level=4, quest=526, gold=40, xp=186, checkmarks=7)
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

    hero6 = ch.Character('Singularity', 'Doomstalker', owner1, level=3, quest=530)
    hero6.addOwnerPerk(remove_2_minus_1)
    hero6.addPerk(remove_2_minus_1)
    hero6.addPerk(add_2_roll_plus_1)
    party.addMember(hero6)

    hero7 = ch.Character('Red', 'Quartermaster', owner2, level=3, quest=522)
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

    hero8 = ch.Character('Ignus', 'Elementalist', owner4, level=1, gold=60, xp=95, quest=524)
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

    hero9 = ch.Character('Playgirl', 'Plagueherald', owner3, level=1, gold=75, xp=150, quest=520)
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

    hero10 = ch.Character('Hayha', 'Nightshroud', owner2, level=1, gold=90, xp=210, quest=518)
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
    party.heroBuyItem("Rabid Cicada", "Jade Falcon")
    
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

    hero11 = ch.Character('RatManBearPig', 'BeastTyrant', owner4, level=1, gold=90, xp=210, quest=527)
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

    # Failed Scenario #38
    party.addTreasureLooted(29, 'Singularity')
    party.heroFindItem('Singularity', 'Endurance Footwraps') # Item #97

    party.heroAdjustXP('Hayha', 12)
    party.heroAdjustXP('Playgirl', 4)
    party.heroAdjustXP('Rabid Cicada', 0)
    party.heroAdjustXP('RatManBearPig', 9)
    party.heroAdjustXP('Singularity', 0)
    party.heroAdjustGold('Hayha', 12)
    party.heroAdjustGold('Playgirl', 4)
    party.heroAdjustGold('Rabid Cicada', 24)
    party.heroAdjustGold('RatManBearPig', 4)
    party.heroAdjustGold('Singularity', 8)
    party.heroAdjustCheckmarks('Hayha', 0)
    party.heroAdjustCheckmarks('Playgirl', 0)
    party.heroAdjustCheckmarks('Rabid Cicada', 0)
    party.heroAdjustCheckmarks('RatManBearPig', 0)
    party.heroAdjustCheckmarks('Singularity', 0)

    party.heroSellItem('Singularity', 'Endurance Footwraps')

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



    # UNSURE - do we unlock scenario 26????

    # Next Play Session
    randScenario = party.drawRandomScenario()
    print("Randomed Scenario Event: %d" % randScenario)

    cityEvent = party.drawRandomCityEvent()
    print("Randomed City Event: %d" % cityEvent)
    roadEvent = party.drawRandomRoadEvent()
    print("Randomed Road Event: %d" % roadEvent)


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
