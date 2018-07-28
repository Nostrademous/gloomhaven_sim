'''
'''

from utils import printJson
import character as hero

INERT  = 0
WANING = 1
STRONG = 2

class Scenario():
    def __init__(self, num, name="", level=0):
        self.scenName   = name
        self.scenID     = num
        self.party      = list()
        self.round      = 0
        self.diff_level = level
        self.complete   = False

        # initialize elemental board to INERT
        self._reset_elements()

    def _reset_elements(self):
        self.elements = {
            "air": INERT,
            "dark": INERT,
            "earth": INERT,
            "fire": INERT,
            "ice": INERT,
            "light": INERT
        }

    def setDifficultyLevel(self, value):
        self.diff_level = value

    def addPlayer(self, player):
        print("[scenario :: addPlayer] :: Adding: %s" % (player.getName()))
        try:
            assert isinstance(player, hero.Character)
            self.party.append(player)
        except AssertionError as err:
            print("[addPlayer :: AssertionError]: %s" % err)
            raise

    def calcTrapDamage(self):
        # this is the default damage amount of the trap
        # specific monster/player/scenario rules can hard-specify
        # the amount instead
        return 2 + self.diff_level

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

    def startScenario(self):
        '''All setup for scenario.'''
        print("[startScenario] Scenario: %d -- Implement Me" % (self.scenID))

        # setup each players ability cards for use in scenario
        for hero in self.party:
            hero.scenarioPreparation()

    def endScenario(self, success=False):
        '''All end scenario work.'''
        print("[endScenario] Scenario: %d -- Implement Me" % (self.scenID))

    def prepareTurn(self):
        '''All preparation of turn work.'''
        print("[Scenario %d] Prepare Turn :: Round: %d" % (self.scenID, self.round))

    def executeTurn(self):
        '''All turn execution work.'''
        print("[Scenario %d] Execute Turn :: Round: %d" % (self.scenID, self.round))

    def endTurn(self):
        print("[Scenario %d] End Turn :: Round: %d" % (self.scenID, self.round))
        # update elements
        for k in self.elements.keys():
            if self.elements[k] > INERT:
                self.elements[k] -= 1
        #printJson(self.elements)

        # increment round counter
        self.round += 1

        if self.round >= 9:
            self.complete = True

    def __repr__(self):
        ret  = "Name: %s\n" % self.scenName
        ret += "Difficulty: %d\n" % self.diff_level
        return ret

if __name__ == "__main__":
    scen = Scenario(1)
    scen.endTurn()

    scen.invokeElement('air')
    scen.invokeElement('fire')
    printJson(scen.elements)

    scen.consumeElement('fire')
    scen.endTurn()

    scen.endTurn()
