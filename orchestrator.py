"""
"""

import character as ch
import scenario
import party

_scenarios = {
    "Black Barrows": {
        "Id": 1,
    }
}

def loadScenario(scenarioID, level=1):
    scenName = ''
    if isinstance(scenarioID, str):
        scenName = scenarioID
        scenarioID = _scenarios[scenarioID]["Id"]
    elif isinstance(scenarioID, int):
        for s in _scenarios:
            if _scenarios[s]["Id"] == scenarioID:
                scenName = scen
                break
    scen = scenario.Scenario(scenarioID, name=scenName, level=level)
    print("<Loaded Scenario>\n%s" % scen)
    return scen

def loadPartyIntoScenario(scenario, party):
    scenario.addParty(party)

def runScenario(scenario):
    # start the scenario
    scenario.startScenario()

    # start the round while loop
    while not scenario.complete:
        scenario.prepareTurn()
        scenario.executeTurn()
        scenario.endTurn()

if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    ourParty = party.make_a_party()

    # load the scenario
    scen = loadScenario("Black Barrows")

    # load party into scenario
    loadPartyIntoScenario(scen, ourParty)

    # run scenario
    runScenario(scen)

    # end scenario
    scen.endScenario()
