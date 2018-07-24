'''
'''

import amd

PERK_TYPE_REMOVE    = 1
PERK_TYPE_ADD       = 2
PERK_TYPE_REPLACE   = 3
PERK_TYPE_IGNORE    = 4

_perk_type = {
    "1": "Remove",
    "2": "Add",
    "3": "Replace",
    "4": "Ignore negative scenario effects"
}

class Perk():
    def __init__(self, perkType, numCards=0, cardType1=None, cardType2=None):
        assert str(perkType) in _perk_type.keys()

        self.perkType   = perkType
        self.numCards   = numCards
        self.cardType1  = cardType1
        self.cardType2  = cardType2

    def __repr__(self):
        ret  = '%s' % (_perk_type[str(self.perkType)])
        if self.numCards > 0:
            ret += " %d" % (self.numCards)
        if self.cardType1:
            if self.cardType1.isRolling():
                ret += " rolling"
            ret += " %s" % (self.cardType1)
        if self.cardType2:
            ret += " with %d %s" % (self.numCards, self.cardType2)
        if self.numCards > 0:
            ret += " cards"
        return ret

tinkerer_perk_1     = Perk(PERK_TYPE_REMOVE, 2, amd.amc_m1)
tinkerer_perk_2     = Perk(PERK_TYPE_REPLACE, 1, amd.amc_m2, amd.amc_0)
tinkerer_perk_3     = Perk(PERK_TYPE_ADD, 2, amd.amc_p1)
tinkerer_perk_4     = Perk(PERK_TYPE_ADD, 1, amd.amc_p3)
tinkerer_perk_5     = Perk(PERK_TYPE_ADD, 2, amd.amc_rollfire)
tinkerer_perk_6     = Perk(PERK_TYPE_ADD, 3, amd.amc_rollmuddle)
tinkerer_perk_7     = Perk(PERK_TYPE_ADD, 1, amd.amc_p1wound)
tinkerer_perk_8     = Perk(PERK_TYPE_ADD, 1, amd.amc_p1immobilize)
tinkerer_perk_9     = Perk(PERK_TYPE_ADD, 1, amd.amc_p1h2)
tinkerer_perk_10    = Perk(PERK_TYPE_ADD, 1, amd.amc_0at)
tinkerer_perk_11    = Perk(PERK_TYPE_IGNORE)

tinkerer_perk_deck = list([
    tinkerer_perk_1, tinkerer_perk_1,
    tinkerer_perk_2,
    tinkerer_perk_3,
    tinkerer_perk_4,
    tinkerer_perk_5,
    tinkerer_perk_6,
    tinkerer_perk_7, tinkerer_perk_7,
    tinkerer_perk_8, tinkerer_perk_8,
    tinkerer_perk_9, tinkerer_perk_9,
    tinkerer_perk_10,
    tinkerer_perk_11
])

if __name__ == "__main__":
    for perk in tinkerer_perk_deck:
        print(perk)
