"""
"""

import character as ch
import scenario
import party

_scenarios = {
    "Black Barrows": {
        "Id": 1,
        "Map Tiles": []
    }
}

def loadScenario(scenarioID):
    if isinstance(scenarioID, str):
        scenarioID = _scenarios[scenarioID]
    scen = scenario.Scenario(scenarioID)
    return scen

def loadPartyIntoScenario(scenario, party):
    print("[loadPartyIntoScenario] - IMPLEMENT")
    for hero in party.members:
        scenario.addPlayer(hero)

def runScenario():
    print("[runScenarion] - IMPLEMENT")


if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    # load the scenario
    scen = loadScenario("Black Barrows")

    # create our heroes
    hero1 = ch.Character('Clockwerk', 'Tinkerer', 'Andrzej', level=2, xp=70, gold=49, quest=528, checkmarks=3)
    hero1.addItem('Eagle-Eye Goggles')

    hero2 = ch.Character('Ruby Sweety Pie', 'Brute', 'Danny', level=1, quest=512, gold=20, xp=31, checkmarks=0)
    hero2.addItem('Minor Healing Potion')
    hero2.addItem('Leather Armor')

    hero3 = ch.Character('Evan', 'Spellweaver', 'Evan Teran', level=1, quest=533, gold=59, xp=44, checkmarks=1)
    hero3.addItem('Cloak of Invisibility')
    hero3.addItem('Minor Power Potion')

    hero4 = ch.Character('Bloodfist Stoneborn', 'Cragheart', 'Matt', level=2, quest=531, gold=29, xp=46, checkmarks=1)
    hero4.addItem('Hide Armor')
    hero4.addItem('Minor Stamina Potion')

    hero5 = ch.Character('Rabid Cicada', 'Scoundrel', 'Kyle', level=2, quest=526, gold=33, xp=59, checkmarks=2)
    hero5.addItem('Leather Armor')
    hero5.addItem('Minor Stamina Potion')
    
    # create our party
    ourParty = party.Party("TheBrotherhood")
    ourParty.addMember(hero1)
    ourParty.addMember(hero2)
    ourParty.addMember(hero3)
    ourParty.addMember(hero4)
    ourParty.addMember(hero5)

    # load party into scenario
    loadPartyIntoScenario(scen, ourParty)
