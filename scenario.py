'''
'''

#from multiprocessing import Process
import threading

import global_vars as gv
from utils import printJson, pickRandom
import character as hero
import map
import party
import npc

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
        self.success    = False

        # initialize elemental board to INERT
        self._reset_elements()

        # some scenarios impose negative starting effects
        # on heroes, this variable tracks them
        self.negative_effects = list()

        self.setMap()

        # we previously set the self.party parameter
        # but that does not mean that all members of
        # the party are participating in this scenario
        # so self.scen_members is a list of actual
        # heroes from the party participating in the
        # scenario
        self.scen_members = None

        # set a method to track all actual npcs in the scenario
        self.npcs         = list()
        # set a method to track all actual npc types in the scenario
        self.npc_types    = list()

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

    def setNegativeScenarioEffects(self, negEffects=list()):
        self.negative_effects = negEffects

    def setDifficultyLevel(self, value):
        self.diff_level = value

    def addParty(self, myParty):
        assert isinstance(myParty, party.Party)
        self.party = myParty
        # pick the members of the part in scenario
        self.scen_members = self.pickMembers()

    def addNPC(self, npc):
        assert isinstance(npc, npc.NPC)
        self.npcs.append(npc)

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
        assert len(self.scen_members) >= 2 and len(self.scen_members) <= 4

        # setup each player's ability cards and attack modifier cards for use in scenario
        for hero in self.scen_members:
            hero.scenarioPreparation(self.negative_effects)

        # set num of players participating in scenario
        gv.setNumPlayersInScenario(len(self.scen_members))

        # calculate the scenario difficulty
        self.scen_map.setDifficulty(self.calculateDifficulty())

        # spawn NPCs in starting room
        new_npcs = self.scen_map.spawnStartingRoom()
        self.npcs.extend(new_npcs)

        # spawn players into starting room
        # TODO

    def endScenario(self):
        '''All end scenario work.'''
        print("[endScenario] Scenario: %d -- Implement Me" % (self.scenID))
        if self.success:
            print("Congratulations! Scenario was completed successfully!")
        else:
            print("You have failed the Scenario! Better luck next time...")

    def prepareTurn(self):
        '''All preparation of turn work.'''
        print("[Scenario %d] Prepare Turn :: Round: %d" % (self.scenID, self.round))

        # parallelize hero ability selection
        parallel_funcs = list()

        for hero in self.scen_members:
            t = threading.Thread(target=hero.selectAction)
            parallel_funcs.append(t)

        '''
        # this only works correctly on Unix do to how "fork()" is implemented
        for hero in self.scen_members:
            parallel_funcs.append(Process(target=hero.selectAction()))
        '''

        # start them
        for p in parallel_funcs:
            p.start()

        # join them
        for p in parallel_funcs:
            p.join()

        # now pick NPC actions
        self.npc_types = list()
        for npc in self.npcs:
            if npc.getParentType() not in self.npc_types:
                self.npc_types.append(npc.getParentType())

        for npcType in self.npc_types:
            npcType.prepareTurn()

    def executeTurn(self):
        '''All turn execution work.'''
        print("[Scenario %d] Execute Turn :: Round: %d" % (self.scenID, self.round))

        # sort all player and npc actions in initiative order
        initiative_list = list()
        for npcType in self.npc_types:
            initiative_list.append((npcType.getRoundInitiative(), npcType))
        for hero in self.scen_members:
            initiative_list.append((hero.getRoundInitiative(), hero))
        initiative_list = sorted(initiative_list, key=lambda x: x[0])
        print("Initiative Order: %s" % (initiative_list))

        # execute each unit's actions (including spawns)
        for unit in initiative_list:
            unit[1].executeTurn()
            # end turn for each unit
            unit[1].endTurn()

    def endTurn(self):
        print("[Scenario %d] End Turn :: Round: %d" % (self.scenID, self.round))
        # update elements
        for k in self.elements.keys():
            if self.elements[k] > INERT:
                self.elements[k] -= 1
        #printJson(self.elements)

        # check scenario completion condition
        # TODO
        # self.complete = True
        # self.success = True
        # return

        # check scenario failure condition (all players exhausted)
        scen_failed = True
        for hero in self.scen_members:
            if not hero.isExhausted():
                scen_failed = False
                break
        if scen_failed:
            self.complete = True
            return

        # determine if a character wants to short-rest
        # TODO

        # increment round counter
        self.round += 1

        # FIXME: eventually remove (once everything else is completed)
        # dummy catch to exit while-loop for now
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

