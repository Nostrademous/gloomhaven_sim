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

heroDataJson = {}

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.members = list()
        self.valid_types = list(['brute', 'scoundrel', 'cragheart', 'tinkerer', 'spellweaver', 'mindthief'])
        self.retired_types = list()
        self.party_json['CompletedCityQuests'] = list()
        self.party_json['CompletedRoadQuests'] = list()
        self.party_json['ScenariosCompleted'] = list()
        self.party_json['ScenariosAvailable'] = list()
        self.party_json['TreasuresLooted'] = list()
        self.party_json['GlobalAchievements'] = list()
        self.party_json['PartyAchievements'] = list()
        self.party_json['GloomhavenProsperity'] = { 'Level': 1, 'Checkmarks': 0 }

    def calcAvgLevel(self):
        avgLevel = 0
        for hero in self.members:
            avgLevel += hero.getLevel()
        return int(avgLevel/len(self.members))

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

    def addRoadQuest(self, value):
        try:
            assert value not in self.party_json['CompletedRoadQuests']
            self.party_json['CompletedRoadQuests'].append(value)
        except AssertionError as err:
            print('[addRoadQuest :: AssertionError] %s' % (err))
            raise

    def addCityQuest(self, value):
        try:
            assert value not in self.party_json['CompletedCityQuests']
            self.party_json['CompletedCityQuests'].append(value)
        except AssertionError as err:
            print('[addCityQuest :: AssertionError] %s' % (err))
            raise

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
            json.dump(self.party_json, outfile)

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
    party.addCityQuest(4)
    party.addCityQuest(18)
    party.addRoadQuest(7)
    party.addRoadQuest(25)
    party.addScenarioCompleted(1)
    party.addScenarioCompleted(2)
    party.addScenarioCompleted(3)
    party.addScenarioAvailable(4)
    party.addScenarioAvailable(8)
    party.addScenarioAvailable(9)
    party.addScenarioAvailable(68)
    party.addProsperityCheckmark()
    party.addProsperityCheckmark()
    #party.retireType('tinkerer')

    hero1 = ch.Character('Clockwerk', 'Tinkerer', 'Andrzej', level=2, xp=70, gold=49, quest=528, checkmarks=3)
    hero1.addItem('Eagle-Eye Goggles')
    hero1.addPerk()
    hero1.addPerk()
    party.addMember(hero1)

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', 'Danny', level=1, quest=512, gold=20, xp=31, checkmarks=0)
    hero2.addItem('Boots of Striding')
    hero2.addItem('Minor Healing Potion')
    hero2.addItem('Leather Armor')
    party.addMember(hero2)

    hero3 = ch.Character('Evan', 'Spellweaver', 'Evan Teran', level=1, quest=533, gold=59, xp=44, checkmarks=1)
    hero3.addItem('Cloak of Invisibility')
    hero3.addItem('Minor Power Potion')
    party.addMember(hero3)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', 'Matt', level=2, quest=531, gold=29, xp=46, checkmarks=1)
    hero4.addItem('Hide Armor')
    hero4.addItem('Boots of Striding')
    hero4.addItem('Minor Stamina Potion')
    hero4.addPerk()
    party.addMember(hero4)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', 'Kyle', level=2, quest=526, gold=33, xp=59, checkmarks=2)
    hero5.addItem('Leather Armor')
    hero5.addItem('Poison Dagger')
    hero5.addItem('Heater Shield')
    hero5.addItem('Minor Stamina Potion')
    hero5.addPerk()
    party.addMember(hero5)

    printJson(party)

    #print("Avg Level: ", party.calcAvgLevel())
    party.saveParty()

    party.loadParty('TheBrotherhood')
    printJson(party)
