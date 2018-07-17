'''
'''

import json
import character as hero

def printParty(partyObj):
    print(json.dumps(partyObj.getJson(), indent=4, sort_keys=True))

class Party():
    def __init__(self, name):
        self.party_json = {}
        self.party_json['PartyName'] = name
        self.characters = list()

    def addCharacter(self, name):
        self.characters.append(hero.Character(name))

        self.party_json['Characters'] = {}
        for k,v in enumerate(self.characters):
            self.party_json['Characters'][v.getName()] = v.getJson()

    def getJson(self):
        return self.party_json

    def saveParty(self):
        with open('%s_party.json' % self.party_json['PartyName'], 'w') as outfile:
            json.dump(self.party_json, outfile)

    def loadParty(self, name):
        self.__init__(name)
        
        with open('%s_party.json' % name) as infile:
            self.party_json = json.load(infile)

        for k,v in enumerate(self.party_json['Characters']):
            self.characters.append(hero.Character(v))

if __name__ == "__main__":
    party = Party('Test')
    party.addCharacter('John')
    party.saveParty()
    party.addCharacter('Beth')
    printParty(party)
    party.loadParty('Test')
    printParty(party)