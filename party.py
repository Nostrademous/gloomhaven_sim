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
from global_vars import starting_hero_types, calculateShopModifier, calculateTrapDamage, calculateHazardDamage, calculateMonsterLevel, calculateGoldConversion, calculateBonusExperience

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
        self.party_json['ScenariosCompleted'] = list()
        self.party_json['ScenariosBlocked'] = list()
        self.party_json['ScenariosAvailable'] = list()
        self.party_json['TreasuresLooted'] = list()
        self.party_json['GlobalAchievements'] = list()
        self.party_json['PartyAchievements'] = list()
        self.party_json['GloomhavenProsperity'] = { 'Level': 1, 'Checkmarks': 0, 'Count': 0 }
        self.party_json['SanctuaryDonations'] = 0
        self.party_json['PartyEnhancements'] = dict()
        
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

    def addGlobalAchievement(self, text):
        self.party_json['GlobalAchievements'].append(text)
        print("\nGlobal Achievement: '%s' obtained!!!" % (text))

    def addPartyAchievement(self, text):
        self.party_json['PartyAchievements'].append(text)
        print("\nParty Achievement: '%s' obtained!!!" % (text))

    def addScenarioCompleted(self, value):
        self.party_json['ScenariosCompleted'].append(value)
        print("\nScenarion #%d Completed!" % (value))

    def addScenarioAvailable(self, value):
        self.party_json['ScenariosAvailable'].append(value)
        print("New Scenarion Available: %d" % (value))

    def addScenarioBlocked(self, value):
        self.party_json['ScenariosBlocked'].append(value)
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

    def addHeroType(self, extraType):
        extraType = extraType.lower()
        assert extraType not in self.valid_hero_types
        self.valid_hero_types.append(extraType)

    def unlockHero(self, strHeroType):
        strHeroType = strHeroType.lower()
        # make hero available to pick again
        assert strHeroType not in self.valid_hero_types
        self.valid_hero_types.append(strHeroType)
        
    def retireHero(self, heroObj):
        for member in self.members:
            if heroObj.getName() is member.getName():
                print("\n<><> Retiring '%s'!!!\n" % member.getName())
                member.retire()
                self.addProsperityCheckmark('%s retirement' % heroObj.getName())
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

            self.claimHeroType(heroObj.getType())
            print("Added '%s - %s' to the party!" % (heroObj.getName(), heroObj.getType()))
        except:
            print("[addMember - Assertion Failed]")
            print("\tAttempted adding '%s'" % (heroObj.getType()))
            print('\tValidTypes: %s' % str(party.valid_hero_types))
            print('\tRetiredTypes: %s' % str(party.retired_types))
            pass

    def addProsperityCheckmark(self, reason='', cnt=1):
        self.party_json['GloomhavenProsperity']['Count'] += cnt

        count_per_increment = [4 + i for i in range(0,9)]
        count_req = [sum(count_per_increment[:i]) for i in range(0,9)]
        curr_cnt = self.party_json['GloomhavenProsperity']['Count']
        for index, value in enumerate(count_req):
            if curr_cnt < value:
                break
        if reason != '':
            print("Gloomhaven gains Prosperity Checkmark :: Reason: '%s'" % (reason))
        else:
            print("Gloomhaven gains Prosperity Checkmark")
        if index > self.party_json['GloomhavenProsperity']['Level']:
            print("\nGLOOMHAVEN LEVELED UP TO %d!!!!\n" % (index))
        self.party_json['GloomhavenProsperity']['Level'] = index
        self.party_json['GloomhavenProsperity']['Checkmarks'] = curr_cnt - count_req[index-1]

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
            if heroObj.canLevel():
                print("\n<><> %s CAN LEVEL UP to %d\n" % (strHero, heroObj.level+1))
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

    def heroBuyItem(self, strHero, strItemName, adjGold=True):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.buyItem(strItemName, adjustGold=adjGold)
            self.party_json['Members'][heroObj.getName()] = heroObj.getJson()
            print("%s buys item [%s] :: gold remaining: %d" % (strHero, strItemName, heroObj.gold))
        else:
            raise Exception('party::heroBuyItem', 'Failed to Find Hero: "%s"' % (strHero))
    
    def heroSellItem(self, strHero, strItemName, adjGold=True):
        heroIndex = self.getHeroIndexByName(strHero)
        if heroIndex >= 0:
            heroObj = self.members[heroIndex]
            heroObj.sellItem(strItemName)
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
            heroObj.level += 1
            print("<><> %s Levels Up to %d" % (strHero, heroObj.getLevel()))
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
            if heroObj.getName() == strName:
                return index
        return -1

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
    party.addTreasureLooted(15) # ItemID:45 "Pendant of Dark Pacts"
    party.addTreasureLooted(26)
    party.addTreasureLooted(28) # +15 Gold - Kyle
    party.addTreasureLooted(38)
    party.addTreasureLooted(46)
    party.addTreasureLooted(51)
    party.addTreasureLooted(60) # ItemID: 113 "Skullbane Axe" - Danny
    party.addTreasureLooted(65)
    party.addTreasureLooted(67)

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
    hero3.buyItem('Cloak of Invisibility', adjustGold=False)
    hero3.buyItem('Minor Power Potion', adjustGold=False)
    hero3.buyItem('Eagle-Eye Goggles', adjustGold=False)
    hero3.buyItem('Piercing Bow', adjustGold=False)
    hero3.addCheckmarkPerk(add_2_plus_1)
    hero3.addPerk(add_2_plus_1)
    hero3.addCheckmarkPerk(add_1_plus_1_wound)
    hero3.addPerk(add_1_plus_2_fire)
    hero3.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero3)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', owner4, level=4, quest=531, gold=32, xp=203, checkmarks=8)
    hero4.buyItem('Hide Armor', adjustGold=False)
    hero4.buyItem('Boots of Striding', adjustGold=False)
    hero4.buyItem('Minor Stamina Potion', adjustGold=False)
    hero4.buyItem('Horned Helm', adjustGold=False)
    hero4.buyItem('Heater Shield', adjustGold=False)
    hero4.addCheckmarkPerk(ignore_item_perk)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addCheckmarkPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(remove_4_0)
    party.addMember(hero4)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', owner5, level=4, quest=526, gold=40, xp=186, checkmarks=7)
    hero5.buyItem('Leather Armor', adjustGold=False)
    hero5.buyItem('Poison Dagger', adjustGold=False)
    hero5.buyItem('Winged Shoes', adjustGold=False)
    hero5.buyItem('Minor Stamina Potion', adjustGold=False)
    hero5.buyItem('Ring of Skulls', adjustGold=False)
    hero5.addCheckmarkPerk(ignore_scen_perk)
    hero5.addPerk(remove_2_minus_1)
    hero5.addCheckmarkPerk(replace_minus_2_with_0)
    hero5.addPerk(remove_2_minus_1)
    hero5.addPerk(replace_minus_1_with_plus_1)
    party.addEnhancement('Rabid Cicada', 102, "Bottom", 'Bless on Invisibility') # 100gold paid
    party.addMember(hero5)

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
    hero7.addOwnerPerk(ignore_scen_perk_add_2_plus_1)
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
    #party.addItemToGloomhaven('Storm Blade')
    party.heroAdjustGold('Rabid Cicada', -1)
    party.heroAdjustGold('Bloodfist Stoneborn', -1)
    party.heroAdjustGold('Evan', -1)
    party.heroAdjustGold('Singularity', -1)
    party.heroAdjustGold('Red', -1)
    party.completeRoadEvent(29)

    party.addTreasureLooted(50, 'Rabid Cicada')
    party.heroBuyItem('Rabid Cicada', 'Second Skin', adjGold=False)

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
    party.heroAdjustCheckmarks('Red', 1)

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
