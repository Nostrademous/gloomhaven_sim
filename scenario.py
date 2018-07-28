'''
'''

from utils import printJson

INERT  = 0
WANING = 1
STRONG = 2

class Scenario():
    def __init__(self, num):
        self.id = num
        self.party = list()
        self.round = 0
        self.diff_level = 0

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

    def startScenarion(self):
        '''All setup for scenario.'''
        print("[startScenario] Scenario: %d -- Implement Me" % (self.id))

    def endScenario(self, success=False):
        '''All end scenario work.'''
        print("[endScenario] Scenario: %d -- Implement Me" % (self.id))

    def prepareTurn(self):
        '''All preparation of turn work.'''
        print("[Scenario %d] Prepare Turn :: Round: %d" % (self.id, self.round))

    def executeTurn(self):
        '''All turn execution work.'''
        print("[Scenario %d] Execute Turn :: Round: %d" % (self.id, self.round))

    def endTurn(self):
        print("[Scenario %d] End Turn :: Round: %d" % (self.id, self.round))
        # update elements
        for k in self.elements.keys():
            if self.elements[k] > INERT:
                self.elements[k] -= 1
        #printJson(self.elements)

        # increment round counter
        self.round += 1

if __name__ == "__main__":
    scen = Scenario(1)
    scen.endTurn()

    scen.invokeElement('air')
    scen.invokeElement('fire')
    printJson(scen.elements)

    scen.consumeElement('fire')
    scen.endTurn()

    scen.endTurn()
