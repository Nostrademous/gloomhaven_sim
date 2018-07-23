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

    def calcAvgLevel(self):
        avgLevel = 0
        for hero in self.members:
            avgLevel += hero.getLevel()
        return int(avgLevel/len(self.members))
        
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
            assert heroObj.getAttr('type') in self.valid_types

            self.members.append(heroObj)
            self.party_json['Members'] = {}
            for k,v in enumerate(self.members):
                self.party_json['Members'][v.getType()] = v.getJson()
            
            self.removeValidType(heroObj.getAttr('type'))
            print("Added '%s - %s' to the party!" % (heroObj.getName(), heroObj.getType()))
        except:
            print("[addMember - Assertion Failed]")
            print("\tAttempted adding '%s'" % (heroObj.getAttr('type')))
            print('\tValidTypes: %s' % str(party.valid_types))
            print('\tRetiredTypes: %s' % str(party.retired_types))
            pass

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
                self.members.append(ch.createCharacter(heroData['name'], heroData['type'], heroData['owner']))

if __name__ == "__main__":
    import global_vars as gv
    gv.init() # call only once

    party = Party('TheBrotherhood')
    party.addCityQuest(4)
    party.addCityQuest(18)
    party.addRoadQuest(7)
    party.addRoadQuest(25)
    #party.retireType('tinkerer')

    hero1 = ch.Character('Clockwerk', 'Tinkerer', 'Andrzej', level=2)
    party.addMember(hero1)
    party.saveParty()

    hero2 = ch.Character('Evan', 'Spellweaver', 'Evan Teran')
    party.addMember(hero2)
    printJson(party)

    print("Avg Level: ", party.calcAvgLevel())
    
    party.loadParty('TheBrotherhood')
    printJson(party)
