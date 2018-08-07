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

if __name__ == "__main__":
    import global_vars as gv
    gv.init() # call only once

    party = Party('TheBrotherhood')
    party.addGlobalAchievement('City Rule: Militaristic')
    party.addPartyAchievement('First Steps')
    party.addPartyAchievement("Jekserah's Plans")
    party.addPartyAchievement("Tremors")
    
    party.completeCityEvent(4)
    party.completeCityEvent(15)
    party.completeCityEvent(18)
    party.completeCityEvent(73)

    party.unlockCityEvent(73)

    party.completeRoadEvent(7)
    party.completeRoadEvent(11)
    party.completeRoadEvent(17)
    party.completeRoadEvent(25)

    party.addScenarioCompleted(1)
    party.addScenarioCompleted(2)
    party.addScenarioCompleted(3)
    party.addScenarioCompleted(4)
    party.addScenarioCompleted(5)

    party.addScenarioAvailable(6)
    party.addScenarioAvailable(8)
    party.addScenarioAvailable(9)
    party.addScenarioAvailable(10)
    party.addScenarioAvailable(14)
    party.addScenarioAvailable(19)
    party.addScenarioAvailable(68)
    party.addScenarioAvailable(84)

    party.addProsperityCheckmark()
    party.addProsperityCheckmark()

    party.addTreasureLooted(4)
    party.addTreasureLooted(7)
    party.addTreasureLooted(38)
    party.addTreasureLooted(46)
    party.addTreasureLooted(65)
    party.addTreasureLooted(67)

    hero1 = ch.Character('Clockwerk', 'Tinkerer', 'Andrzej', level=2, xp=102, gold=38, quest=528, checkmarks=5)
    hero1.addItem('Eagle-Eye Goggles')
    hero1.addItem('Minor Power Potion')
    hero1.addItem('Winged Boots')
    hero1.addPerk(ignore_scen_perk)
    hero1.addPerk(remove_2_minus_1)
    #hero1.addPerk()
    party.addMember(hero1)

    hero1.scenarioPreparation()
    print(hero1.ability_deck)

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', 'Danny', level=2, quest=512, gold=46, xp=63, checkmarks=2)
    hero2.addItem('Boots of Striding')
    hero2.addItem('Minor Healing Potion')
    hero2.addItem('Leather Armor')
    hero2.addItem('Iron Helmet')
    hero2.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero2)

    hero3 = ch.Character('Evan', 'Spellweaver', 'Evan Teran', level=2, quest=533, gold=59, xp=80, checkmarks=3)
    hero3.addItem('Cloak of Invisibility')
    hero3.addItem('Minor Power Potion')
    hero3.addItem('Eagle-Eye Goggles')
    hero3.addPerk(add_2_plus_1)
    #hero3.addPerk()
    party.addMember(hero3)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', 'Matt', level=2, quest=531, gold=24, xp=80, checkmarks=3)
    hero4.addItem('Hide Armor')
    hero4.addItem('Boots of Striding')
    hero4.addItem('Minor Stamina Potion')
    hero4.addPerk(ignore_item_perk)
    #hero4.addPerk()
    party.addMember(hero4)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', 'Kyle', level=2, quest=526, gold=48, xp=79, checkmarks=2)
    hero5.addItem('Leather Armor')
    hero5.addItem('Poison Dagger')
    hero5.addItem('Heater Shield')
    hero5.addItem('Minor Stamina Potion')
    hero5.addPerk(ignore_scen_perk)
    party.addMember(hero5)

    party.makeSanctuaryDonation()

    printJson(party)
    print('\n\n\n')

    #print("Avg Level: ", party.calcAvgLevel())
    party.saveParty()

    party.loadParty('TheBrotherhood')
    printJson(party)
