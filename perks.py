'''
'''

import amd

PERK_TYPE_REMOVE        = 1
PERK_TYPE_ADD           = 2
PERK_TYPE_REPLACE       = 3
PERK_TYPE_IGNORE_SCEN   = 4
PERK_TYPE_IGNORE_ITEM   = 5

_perk_type = {
    "1": "Remove",
    "2": "Add",
    "3": "Replace",
    "4": "Ignore negative scenario effects",
    "5": "Ignore negative item effects"
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
            ret += " %s" % (self.cardType1)
        if self.cardType2:
            ret += " with %d %s" % (self.numCards, self.cardType2)
        if self.numCards > 0:
            ret += " cards"
        return ret

# used by multiple classes
ignore_scen_perk        = Perk(PERK_TYPE_IGNORE_SCEN)
ignore_item_perk        = Perk(PERK_TYPE_IGNORE_ITEM)

remove_2_minus_1        = Perk(PERK_TYPE_REMOVE, 2, amd.amc_m1)
remove_4_0              = Perk(PERK_TYPE_REMOVE, 4, amd.amc_0)

replace_minus_2_with_0      = Perk(PERK_TYPE_REPLACE, 1, amd.amc_m2, amd.amc_0)
replace_minus_1_with_plus_1 = Perk(PERK_TYPE_REPLACE, 1, amd.amc_m1, amd.amc_p1)
replace_0_with_plus_2       = Perk(PERK_TYPE_REPLACE, 1, amd.amc_0, amd.amc_p2)

add_2_plus_1            = Perk(PERK_TYPE_ADD, 2, amd.amc_p1)
add_2_roll_plus_1       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_p1)
add_1_plus_3            = Perk(PERK_TYPE_ADD, 1, amd.amc_p3)

add_1_0_stun            = Perk(PERK_TYPE_ADD, 1, amd.amc_0_stun)
add_1_roll_invis        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_invis)
add_1_roll_stun         = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_stun)
add_2_roll_muddle       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_muddle)
add_3_roll_muddle       = Perk(PERK_TYPE_ADD, 3, amd.amc_roll_muddle)
add_2_roll_poison       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_poison)
add_1_plus_1_immobilize = Perk(PERK_TYPE_ADD, 1, amd.amc_p1_immobilize)
add_1_plus_1_wound      = Perk(PERK_TYPE_ADD, 1, amd.amc_p1_wound)
add_2_roll_pierce3      = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_pierce_3)

# elemental based
add_1_roll_air          = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_air)
add_1_roll_dark         = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_dark)
add_1_roll_earth        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_earth)
add_2_roll_fire         = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_fire)
add_1_roll_light        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_light)

add_1_plus_1_curse      = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_1_curse)

add_1_plus_2_fire       = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_2_fire)
add_1_plus_2_ice        = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_2_ice)

# class specific perks
tinkerer_perk_9     = Perk(PERK_TYPE_ADD, 1, amd.amc_p1h2)
tinkerer_perk_10    = Perk(PERK_TYPE_ADD, 1, amd.amc_0at)

brute_perk_deck = list([
    remove_2_minus_1,
    replace_minus_1_with_plus_1,
    add_2_plus_1, add_2_plus_1,
    add_1_plus_3,
    #5,
    #6,
    add_1_roll_stun, add_1_roll_stun,
    #8,
    #9,
    #10,
    ignore_scen_perk
])

cragheart_perk_deck = list([
    remove_4_0,
    replace_minus_1_with_plus_1, replace_minus_1_with_plus_1, replace_minus_1_with_plus_1,
    #3,
    add_1_plus_1_immobilize, add_1_plus_1_immobilize,
    #5,
    #6,
    #7,
    #8,
    ignore_item_perk,
    ignore_scen_perk
])

mindthief_perk_deck = list([
    ignore_scen_perk
])

scoundrel_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    remove_4_0,
    replace_minus_2_with_0,
    replace_minus_1_with_plus_1,
    replace_0_with_plus_2, replace_0_with_plus_2,
    add_2_roll_plus_1, add_2_roll_plus_1,
    add_2_roll_pierce3,
    add_2_roll_poison, add_2_roll_poison,
    add_2_roll_muddle,
    add_1_roll_invis,
    ignore_scen_perk
])

spellweaver_perk_deck = list([
    remove_4_0,
    replace_minus_1_with_plus_1, replace_minus_1_with_plus_1,
    add_2_plus_1, add_2_plus_1,
    add_1_0_stun,
    add_1_plus_1_wound,
    add_1_plus_1_immobilize,
    add_1_plus_1_curse,
    add_1_plus_2_fire, add_1_plus_2_fire,
    add_1_plus_2_ice, add_1_plus_2_ice,
    [add_1_roll_earth, add_1_roll_air],
    [add_1_roll_light, add_1_roll_dark]
])

tinkerer_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    replace_minus_2_with_0,
    add_2_plus_1,
    add_1_plus_3,
    add_2_roll_fire,
    add_3_roll_muddle,
    add_1_plus_1_wound, add_1_plus_1_wound,
    add_1_plus_1_immobilize, add_1_plus_1_immobilize,
    tinkerer_perk_9, tinkerer_perk_9,
    tinkerer_perk_10,
    ignore_scen_perk
])

def getPerkSelections(class_type):
    class_type = class_type.lower()
    if class_type == "brute":
        return brute_perk_deck
    elif class_type == "cragheart":
        return cragheart_perk_deck
    elif class_type == "mindthief":
        return mindthief_perk_deck
    elif class_type == "scoundrel":
        return scoundrel_perk_deck
    elif class_type == "spellweaver":
        return spellweaver_perk_deck
    elif class_type == "tinkerer":
        return tinkerer_perk_deck
    else:
        raise Exception("[getPerkSelection]", "UNKNOWN CLASS TYPE")

if __name__ == "__main__":
    for perk in tinkerer_perk_deck:
        print(perk)

    print('\nScoundrel')
    for perk in scoundrel_perk_deck:
        print(perk)

    print('\nSpellweaver')
    for perk in spellweaver_perk_deck:
        print(perk)
