'''
    A Gloomhaven Party has the following attributes:
        # Stage 1 implementation
        Name: (name of party)
        Members: (list class characters.py)
        
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

def printParty(partyObj):
    print(json.dumps(partyObj.getJson(), indent=4, sort_keys=True))

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.members = list()

    def addMember(self, characterObj):
        self.members.append(characterObj)

        self.party_json['Members'] = {}
        for k,v in enumerate(self.members):
            self.party_json['Members'][v.getType()] = v.getJson()

    def getJson(self):
        return self.party_json

    def saveParty(self):
        with open('%s_party.json' % self.party_json['PartyName'], 'w') as outfile:
            json.dump(self.party_json, outfile)

    def loadParty(self, name):
        self.__init__(name)
        
        with open('%s_party.json' % name) as infile:
            self.party_json = json.load(infile)

        for k,v in enumerate(self.party_json['Members']):
            heroData = self.party_json['Members'][v]
            self.members.append(ch.createCharacter(heroData['name'], heroData['type'], heroData['owner']))


if __name__ == "__main__":
    party = Party('TheBrotherhood')
    hero1 = ch.createCharacter('Clockwerk', 'Tinkerer', 'Andrzej')
    
    party.addMember(hero1)
    party.saveParty()

    hero2 = ch.createCharacter('Evan', 'Spellweaver', 'Evan Teran')
    party.addMember(hero2)
    
    printParty(party)

    party.loadParty('TheBrotherhood')
    printParty(party)