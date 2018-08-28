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

import json
import character as ch
from utils import printJson
from perks import *

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.members = list()
        self.valid_types = list(['brute', 'scoundrel', 'cragheart', 'tinkerer', 'spellweaver', 'mindthief'])
        self.retired_types = list()
        self.party_json['UnlockedCityEvents'] = list()
        self.party_json['CompletedCityEvents'] = list()
        self.party_json['UnlockedRoadEvents'] = list()
        self.party_json['CompletedRoadEvents'] = list()
        self.party_json['ScenariosCompleted'] = list()
        self.party_json['ScenariosAvailable'] = list()
        self.party_json['TreasuresLooted'] = list()
        self.party_json['GlobalAchievements'] = list()
        self.party_json['PartyAchievements'] = list()
        self.party_json['GloomhavenProsperity'] = { 'Level': 1, 'Checkmarks': 0 }
        self.party_json['SanctuaryDonations'] = 0

    def makeSanctuaryDonation(self):
        self.party_json['SanctuaryDonations'] += 1

    def calcAvgLevel(self):
        avgLevel = 0
        for hero in self.members:
            avgLevel += hero.getLevel()
        return int(avgLevel/len(self.members))

    def addGlobalAchievement(self, text):
        self.party_json['GlobalAchievements'].append(text)

    def addPartyAchievement(self, text):
        self.party_json['PartyAchievements'].append(text)

    def addScenarioCompleted(self, value):
        self.party_json['ScenariosCompleted'].append(value)

    def addScenarioAvailable(self, value):
        self.party_json['ScenariosAvailable'].append(value)

    def addTreasureLooted(self, value):
        assert value not in self.party_json['TreasuresLooted']
        try:
            self.party_json['TreasuresLooted'].append(value)
        except AssertionError as err:
            print("[addTreasureLooted :: AssertionError] %s" % (err))
            raise

    def completeRoadEvent(self, value):
        try:
            assert value not in self.party_json['CompletedRoadEvents']
            self.party_json['CompletedRoadEvents'].append(value)
        except AssertionError as err:
            print('[completeRoadEvent:: AssertionError] %s' % (err))
            raise

    def completeCityEvent(self, value):
        try:
            assert value not in self.party_json['CompletedCityEvents']
            self.party_json['CompletedCityEvents'].append(value)
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
        pool = [i for i in range(1,maxID)]
        for unlocked in self.party_json['UnlockedCityEvents']:
            pool.append(unlocked)
        for done in self.party_json['CompletedCityEvents']:
            pool.remove(done)
        drawn = pickRandom(pool)
        self.completeCityEvent(drawn)
        return drawn

    def drawRandomRoadEvent(self, maxID=30):
        pool = [i for i in range(1,maxID)]
        for unlocked in self.party_json['UnlockedRoadEvents']:
            pool.append(unlocked)
        for done in self.party_json['CompletedRoadEvents']:
            pool.remove(done)
        drawn = pickRandom(pool)
        self.completeRoadEvent(drawn)
        return drawn

    def addValidType(self, extraType):
        extraType = extraType.lower()
        assert extraType not in self.valid_types
        assert extraType not in self.retired_types
        self.valid_types.append(extraType)

    def removeValidType(self, extraType):
        extraType = extraType.lower()
        assert extraType in self.valid_types
        self.valid_types.remove(extraType)

    def retireType(self, retireType):
        retireType = retireType.lower()
        assert retireType in self.valid_types
        assert retireType not in self.retired_types
        self.retired_types.append(retireType)
        self.valid_types.remove(retireType)

    def addMember(self, heroObj):
        try:
            assert heroObj.getType() in self.valid_types

            self.members.append(heroObj)
            self.party_json['Members'] = {}
            for k,v in enumerate(self.members):
                self.party_json['Members'][v.getType()] = v.getJson()

            self.removeValidType(heroObj.getType())
            print("Added '%s - %s' to the party!" % (heroObj.getName(), heroObj.getType()))
        except:
            print("[addMember - Assertion Failed]")
            print("\tAttempted adding '%s'" % (heroObj.getType()))
            print('\tValidTypes: %s' % str(party.valid_types))
            print('\tRetiredTypes: %s' % str(party.retired_types))
            pass

    def addProsperityCheckmark(self):
        self.party_json['GloomhavenProsperity']['Checkmarks'] += 1
        if self.party_json['GloomhavenProsperity']['Checkmarks'] == 4:
            self.party_json['GloomhavenProsperity']['Level'] += 1
            self.party_json['GloomhavenProsperity']['Checkmarks'] += 1

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

    party.setReputation(1)

    party.addGlobalAchievement('City Rule: Militaristic')
    party.addGlobalAchievement('The Power of Enhancement')
    party.addGlobalAchievement('The Merchant Flees')

    party.addPartyAchievement('First Steps')
    party.addPartyAchievement("Jekserah's Plans")
    party.addPartyAchievement("Tremors")
    party.addPartyAchievement("A Demon's Errand")

    party.completeCityEvent(4)
    party.completeCityEvent(15)
    party.completeCityEvent(17)
    party.completeCityEvent(18)
    party.completeCityEvent(19)
    party.completeCityEvent(73)

    #party.unlockCityEvent(73)

    party.completeRoadEvent(7)
    party.completeRoadEvent(11)
    party.completeRoadEvent(17)
    party.completeRoadEvent(25)

    party.addScenarioCompleted(1)
    party.addScenarioCompleted(2)
    party.addScenarioCompleted(3)
    party.addScenarioCompleted(4)
    party.addScenarioCompleted(5)
    party.addScenarioCompleted(8)
    party.addScenarioCompleted(10)
    party.addScenarioCompleted(14)

    party.addScenarioAvailable(6)
    party.addScenarioAvailable(7)
    party.addScenarioAvailable(9)
    party.addScenarioAvailable(13)
    party.addScenarioAvailable(14)
    party.addScenarioAvailable(19)
    party.addScenarioAvailable(21)
    party.addScenarioAvailable(22)
    party.addScenarioAvailable(66)
    party.addScenarioAvailable(68)
    party.addScenarioAvailable(81)
    party.addScenarioAvailable(84)

    party.addProsperityCheckmark()
    party.addProsperityCheckmark()

    party.addTreasureLooted(4)
    party.addTreasureLooted(7)
    party.addTreasureLooted(11) # ItemID:85 "Wand of Inferno"
    party.addTreasureLooted(26)
    party.addTreasureLooted(38)
    party.addTreasureLooted(46)
    party.addTreasureLooted(51)
    party.addTreasureLooted(65)
    party.addTreasureLooted(67)

    hero1 = ch.Character('Clockwerk', 'Tinkerer', 'Andrzej', level=3, xp=146, gold=52, quest=528, checkmarks=6)
    hero1.buyItem('Eagle-Eye Goggles', adjustGold=False)
    hero1.buyItem('Minor Power Potion', adjustGold=False)
    hero1.buyItem('Winged Shoes', adjustGold=False)
    hero1.addPerk(ignore_scen_perk)
    hero1.addPerk(remove_2_minus_1)
    hero1.addPerk(add_1_plus_3)
    party.addMember(hero1)
    hero1.scenarioPreparation()

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', 'Danny', level=3, quest=512, gold=55, xp=100, checkmarks=3)
    hero2.buyItem('Boots of Striding', adjustGold=False)
    hero2.buyItem('Minor Healing Potion', adjustGold=False)
    hero2.buyItem('Leather Armor', adjustGold=False)
    hero2.buyItem('Iron Helmet', adjustGold=False)
    hero2.addPerk(replace_minus_1_with_plus_1)
    hero2.addPerk(remove_2_minus_1))
    hero2.addPerk(add_1_plus_3)
    party.addMember(hero2)

    hero3 = ch.Character('Evan', 'Spellweaver', 'Evan Teran', level=3, quest=533, gold=45, xp=148, checkmarks=8)
    hero3.buyItem('Cloak of Invisibility', adjustGold=False)
    hero3.buyItem('Minor Power Potion', adjustGold=False)
    hero3.buyItem('Eagle-Eye Goggles', adjustGold=False)
    hero3.buyItem('Wand of Infernos', adjustGold=False)
    hero3.addPerk(add_2_plus_1)
    hero3.addPerk(add_2_plus_1)
    hero3.addPerk(add_1_plus_1_wound)
    hero3.addPerk(add_1_plus_2_fire)
    party.addMember(hero3)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', 'Matt', level=3, quest=531, gold=39, xp=146, checkmarks=6)
    hero4.buyItem('Hide Armor', adjustGold=False)
    hero4.buyItem('Boots of Striding', adjustGold=False)
    hero4.buyItem('Minor Stamina Potion', adjustGold=False)
    hero4.buyItem('Horned Helm', adjustGold=False)
    hero4.addPerk(ignore_item_perk)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero4)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', 'Kyle', level=3, quest=526, gold=20, xp=128, checkmarks=6)
    hero5.buyItem('Leather Armor', adjustGold=False)
    hero5.buyItem('Poison Dagger', adjustGold=False)
    hero5.buyItem('Heater Shield', adjustGold=False)
    hero5.buyItem('Minor Stamina Potion', adjustGold=False)
    hero5.buyItem('Ring of Skulls', adjustGold=False)
    hero5.addPerk(ignore_scen_perk)
    hero5.addPerk(remove_2_minus_1)
    hero5.addPerk(replace_minus_2_with_0)
    party.addMember(hero5)

    party.makeSanctuaryDonation()
    party.makeSanctuaryDonation()
    party.makeSanctuaryDonation()
    party.makeSanctuaryDonation()

    printJson(party)
    print('\n\n\n')

    #print("Avg Level: ", party.calcAvgLevel())
    party.saveParty()

    return party

if __name__ == "__main__":
    party = make_a_party()
    party.loadParty('TheBrotherhood')
    printJson(party)
