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
        self.owners     = list()
        self.members    = list()
        self.valid_hero_types   = list(['brute', 'scoundrel', 'cragheart', 'tinkerer', 'spellweaver', 'mindthief'])
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

    def adjustReputation(self, amount):
        self.party_json['Reputation'] = min(max(self.party_json['Reputation'] + amount, -20), 20)

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

    def addScenarioBlocked(self, value):
        self.party_json['ScenariosBlocked'].append(value)
        
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

    def addHeroType(self, extraType):
        extraType = extraType.lower()
        assert extraType not in self.valid_hero_types
        self.valid_hero_types.append(extraType)

    def retireHero(self, heroObj):
        self.retireHeroType(hero.getType())

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
                self.party_json['Members'][v.getType()] = v.getJson()

            self.claimHeroType(heroObj.getType())
            print("Added '%s - %s' to the party!" % (heroObj.getName(), heroObj.getType()))
        except:
            print("[addMember - Assertion Failed]")
            print("\tAttempted adding '%s'" % (heroObj.getType()))
            print('\tValidTypes: %s' % str(party.valid_hero_types))
            print('\tRetiredTypes: %s' % str(party.retired_types))
            pass

    def addProsperityCheckmark(self, cnt=1):
        self.party_json['GloomhavenProsperity']['Count'] += cnt

        count_per_increment = [4 + i for i in range(0,9)]
        count_req = [sum(count_per_increment[:i]) for i in range(0,9)]
        curr_cnt = self.party_json['GloomhavenProsperity']['Count']
        for index, value in enumerate(count_req):
            if curr_cnt < value:
                break
        self.party_json['GloomhavenProsperity']['Level'] = index
        self.party_json['GloomhavenProsperity']['Checkmarks'] = curr_cnt - count_req[index-1]

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
    party.completeCityEvent(15)
    party.completeCityEvent(17)
    party.completeCityEvent(18)
    party.completeCityEvent(19)
    party.completeCityEvent(21)
    party.completeCityEvent(27)
    party.completeCityEvent(28)
    party.completeCityEvent(30)
    party.completeCityEvent(73)

    #party.unlockCityEvent(73)
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
    party.addProsperityCheckmark() # +1 from 10 Sanctuary Donations
    party.addProsperityCheckmark()
    party.addProsperityCheckmark() # from Scenario 20

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

    hero1 = ch.Character('Clockwerk', 'Tinkerer', owner1, level=4, xp=225, gold=79, quest=528, checkmarks=10)
    hero1.buyItem('Eagle-Eye Goggles', adjustGold=False)
    hero1.buyItem('Minor Power Potion', adjustGold=False)
    hero1.buyItem('Winged Shoes', adjustGold=False)
    hero1.buyItem('Stun Powder', adjustGold=False)
    hero1.buyItem('Cloak of Invisibility', adjustGold=False)
    hero1.addPerk(ignore_scen_perk)
    hero1.addPerk(remove_2_minus_1)
    hero1.addPerk(add_1_plus_3)
    hero1.addPerk(remove_2_minus_1)
    hero1.addPerk(replace_minus_2_with_0)
    hero1.addPerk(add_1_plus_1_wound)
    party.addMember(hero1)
    hero1.scenarioPreparation()

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', owner2, level=3, quest=512, gold=191, xp=161, checkmarks=5)
    hero2.buyItem('Boots of Striding', adjustGold=False)
    hero2.buyItem('Minor Healing Potion', adjustGold=False)
    hero2.buyItem('Leather Armor', adjustGold=False)
    hero2.buyItem('Iron Helmet', adjustGold=False)
    #hero2.findItem('Skullbane Axe')
    hero2.addPerk(replace_minus_1_with_plus_1)
    hero2.addPerk(remove_2_minus_1)
    hero2.addPerk(add_1_plus_3)
    party.addMember(hero2)

    hero3 = ch.Character('Evan', 'Spellweaver', owner3, level=4, quest=533, gold=39, xp=208, checkmarks=9)
    hero3.buyItem('Cloak of Invisibility', adjustGold=False)
    hero3.buyItem('Minor Power Potion', adjustGold=False)
    hero3.buyItem('Eagle-Eye Goggles', adjustGold=False)
    hero3.buyItem('Piercing Bow', adjustGold=False)
    hero3.addPerk(add_2_plus_1)
    hero3.addPerk(add_2_plus_1)
    hero3.addPerk(add_1_plus_1_wound)
    hero3.addPerk(add_1_plus_2_fire)
    hero3.addPerk(replace_minus_1_with_plus_1)
    party.addMember(hero3)

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', owner4, level=4, quest=531, gold=32, xp=203, checkmarks=8)
    hero4.buyItem('Hide Armor', adjustGold=False)
    hero4.buyItem('Boots of Striding', adjustGold=False)
    hero4.buyItem('Minor Stamina Potion', adjustGold=False)
    hero4.buyItem('Horned Helm', adjustGold=False)
    hero4.buyItem('Heater Shield', adjustGold=False)
    hero4.addPerk(ignore_item_perk)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(replace_minus_1_with_plus_1)
    hero4.addPerk(remove_4_0)
    party.addMember(hero4)

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', owner5, level=4, quest=526, gold=40, xp=186, checkmarks=7)
    hero5.buyItem('Leather Armor', adjustGold=False)
    hero5.buyItem('Poison Dagger', adjustGold=False)
    hero5.buyItem('Heater Shield', adjustGold=False)
    hero5.buyItem('Minor Stamina Potion', adjustGold=False)
    hero5.buyItem('Ring of Skulls', adjustGold=False)
    hero5.addPerk(ignore_scen_perk)
    hero5.addPerk(remove_2_minus_1)
    hero5.addPerk(replace_minus_2_with_0)
    hero5.addPerk(remove_2_minus_1)
    hero5.addPerk(replace_minus_1_with_plus_1)
    #hero5.addEnhancement(card_102, bottom, 'Bless') # 100gold paid
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

    party.addPlayers([owner1, owner2, owner3, owner4, owner5])

    printJson(party)
    print('\n\n\n')

    #print("Avg Level: ", party.calcAvgLevel())
    party.saveParty()

    return party

if __name__ == "__main__":
    party = make_a_party()
    party.loadParty('TheBrotherhood')
    printJson(party)
