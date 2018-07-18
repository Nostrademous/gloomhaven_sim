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
import global_vars as gv
import character as ch

heroDataJson = {}

def loadHeroData(dataFile='hero_data.json'):
    with open(dataFile, 'r') as infile:
        gv.heroDataJson = json.load(infile)

def printParty(partyObj):
    print(json.dumps(partyObj.getJson(), indent=4, sort_keys=True))

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.members = list()
        self.valid_types = list(['brute', 'scoundrel', 'cragheart', 'tinkerer', 'spellweaver', 'mindthief'])
        self.retired_types = list()

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

gv.init() # call only once
if __name__ == "__main__":
    loadHeroData()

    party = Party('TheBrotherhood')
    #party.retireType('tinkerer')

    hero1 = ch.createCharacter('Clockwerk', 'Tinkerer', 'Andrzej')
    party.addMember(hero1)
    party.saveParty()

    hero2 = ch.createCharacter('Evan', 'Spellweaver', 'Evan Teran')
    party.addMember(hero2)
    printParty(party)

    party.loadParty('TheBrotherhood')
    printParty(party)
