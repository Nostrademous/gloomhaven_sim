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

    def endTurn(self):
        print('[Scenario %d] End Turn' % (self.id))
        # update elements
        for k in self.elements.keys():
            if self.elements[k] > INERT:
                self.elements[k] -= 1
        #printJson(self.elements)

if __name__ == "__main__":
    scen = Scenario(0)
    scen.endTurn()

    scen.invokeElement('air')
    scen.invokeElement('fire')
    printJson(scen.elements)

    scen.consumeElement('fire')
    scen.endTurn()

    scen.endTurn()
