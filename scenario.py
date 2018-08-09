'''
'''

from multiprocessing import Process

import global_vars as gv
from utils import printJson, pickRandom
import character as hero
import map
import party

INERT  = 0
WANING = 1
STRONG = 2

class Scenario():
    def __init__(self, num, name="", level=0):
        self.scenName   = name
        self.scenID     = num
        self.party      = None
        self.round      = 0
        self.diff_level = level
        self.complete   = False

        # initialize elemental board to INERT
        self._reset_elements()

        self.setMap()

        # we previously set the self.party parameter
        # but that does not mean that all members of
        # the party are participating in this scenario
        # so self.scen_members is a list of actual
        # heroes from the party participating in the 
        # scenario
        self.scen_members = None

    def _reset_elements(self):
        self.elements = {
            "air": INERT,
            "dark": INERT,
            "earth": INERT,
            "fire": INERT,
            "ice": INERT,
            "light": INERT
        }

    # this creates the map.Map() instance which in turn
    # calls it's preparation callback function (if present)
    # to prepoulate the map with all objects/units
    def setMap(self):
        self.scen_map = map._map_json[str(self.scenID)]
        assert self.scen_map != None

    def setDifficultyLevel(self, value):
        self.diff_level = value

    def addParty(self, myParty):
        assert isinstance(myParty, party.Party)
        self.party = myParty
        # pick the members of the part in scenario
        self.scen_members = self.pickMembers()

    def pickMembers(self, num=4):
        random_members = pickRandom(self.party.members, num)
        print("SELECTED RANDOM MEMBERS\n\n")
        print(random_members)
        return random_members

    def invokeElement(self, name):
        try:
            assert name.lower() in self.elements.keys()
            self.elements[name.lower()] = STRONG
        except AssertionError as err:
            print("[invokeElement :: AssertionError] %s" % err)
            raise

    def consumeElement(self, name):
        try:
            assert name.lower() in self.elements.keys()
            assert self.elements[name.lower()] > INERT
            self.elements[name.lower()] = INERT
        except AssertionError as err:
            print("[consumeElement :: AssertionError] %s" % err)
            raise

    def calculateDifficulty(self, offset=0):
        avgLevel = 0
        for hero in self.scen_members:
            avgLevel += hero.getLevel()
        return int(avgLevel/len(self.scen_members)) + offset

    def startScenario(self):
        '''All setup for scenario.'''
        print("[startScenario] Scenario: %d -- Implement Me" % (self.scenID))

        # setup each players ability cards for use in scenario
        for hero in self.scen_members:
            hero.scenarioPreparation()

        # set num of players participating in scenario
        gv.setNumPlayersInScenario(len(self.scen_members))

        # calculate the scenario difficulty
        self.scen_map.setDifficulty(self.calculateDifficulty())

        # spawn NPCs in starting room
        self.scen_map.spawnStartingRoom()

    def endScenario(self, success=False):
        '''All end scenario work.'''
        print("[endScenario] Scenario: %d -- Implement Me" % (self.scenID))

    def prepareTurn(self):
        '''All preparation of turn work.'''
        print("[Scenario %d] Prepare Turn :: Round: %d" % (self.scenID, self.round))

        # parallelize hero ability selection
        parallel_funcs = list()
        for hero in self.scen_members:
            parallel_funcs.append(Process(target=hero.selectAction()))

        # start them
        for p in parallel_funcs:
            p.start()

        # join them
        for p in parallel_funcs:
            p.join()

    def executeTurn(self):
        '''All turn execution work.'''
        print("[Scenario %d] Execute Turn :: Round: %d" % (self.scenID, self.round))

        # sort all player and npc actions in initiative order

        # execute each unit's actions (including spawns)

            # end turn for each unit

    def endTurn(self):
        print("[Scenario %d] End Turn :: Round: %d" % (self.scenID, self.round))
        # update elements
        for k in self.elements.keys():
            if self.elements[k] > INERT:
                self.elements[k] -= 1
        #printJson(self.elements)

        # check scenario completion condition
        # TODO

        # perfrom endTurn for each hero
        for hero in self.scen_members:
            hero.endTurn()

        # increment round counter
        self.round += 1
        # dummy catch to exist while loop for now
        if self.round >= 9:
            self.complete = True

    def __repr__(self):
        ret  = "Name: %s\n" % self.scenName
        ret += "Difficulty: %d\n" % self.diff_level
        return ret

if __name__ == "__main__":
    scen = Scenario(1, "Black Barrows")
    scen.addParty(party.make_a_party())
    scen.startScenario()

    while not scen.complete:
        scen.prepareTurn()
        scen.executeTurn()
        scen.endTurn()

    scen.endScenario()

