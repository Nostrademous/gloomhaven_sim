'''
'''

import amd

PERK_TYPE_REMOVE            = 1
PERK_TYPE_ADD               = 2
PERK_TYPE_REPLACE           = 3
PERK_TYPE_IGNORE_SCEN       = 4
PERK_TYPE_IGNORE_ITEM       = 5
PERK_TYPE_IGNORE_SCEN_P1    = 6
PERK_TYPE_IGNORE_ITEM_2P1   = 7
PERK_TYPE_IGNORE_SCEN_2P1   = 8


_perk_type = {
    "1": "Remove",
    "2": "Add",
    "3": "Replace",
    "4": "Ignore negative scenario effects",
    "5": "Ignore negative item effects",
    "6": "Ignore negative scenario effects and add +1",
    "7": "Ignore negative item effects and add 2 +1",
    "8": "Ignore negative scenario effects and add 2 +1",
}

class Perk():
    def __init__(self, perkType, numCards=0, cardType1=None, cardType2=None):
        assert str(perkType) in _perk_type.keys()

        self.perkType   = perkType
        self.numCards   = numCards
        self.cardType1  = cardType1
        self.cardType2  = cardType2

    def getJson(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(self, list) and isinstance(other, list):
            for indx, _ in enumerate(self):
                if self[indx].__dict__ != other[indx].__dict__:
                    return False
            return True

        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

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

# we over-load the concept of a perk to account for negative scenario effects
add_3_minus_1           = Perk(PERK_TYPE_ADD, 3, amd.amc_m1)
add_3_curse             = Perk(PERK_TYPE_ADD, 3, amd.amc_curse)

# used by multiple classes
ignore_scen_perk        = Perk(PERK_TYPE_IGNORE_SCEN)
ignore_item_perk        = Perk(PERK_TYPE_IGNORE_ITEM)
ignore_scen_perk_plus_1 = Perk(PERK_TYPE_IGNORE_SCEN_P1)
ignore_item_perk_add_2_plus_1   = Perk(PERK_TYPE_IGNORE_ITEM_2P1)
ignore_scen_perk_2_plus_1 = Perk(PERK_TYPE_IGNORE_SCEN_2P1)

remove_2_0              = Perk(PERK_TYPE_REMOVE, 2, amd.amc_0)
remove_2_minus_1        = Perk(PERK_TYPE_REMOVE, 2, amd.amc_m1)
remove_4_0              = Perk(PERK_TYPE_REMOVE, 4, amd.amc_0)

replace_minus_2_with_0          = Perk(PERK_TYPE_REPLACE, 1, amd.amc_m2, amd.amc_0)
replace_minus_1_with_plus_1     = Perk(PERK_TYPE_REPLACE, 1, amd.amc_m1, amd.amc_p1)
replace_0_with_plus_2           = Perk(PERK_TYPE_REPLACE, 1, amd.amc_0, amd.amc_p2)
replace_2_0_with_2_plus_1       = Perk(PERK_TYPE_REPLACE, 2, amd.amc_0, amd.amc_p1)
replace_2_plus_1_with_2_plus_2  = Perk(PERK_TYPE_REPLACE, 2, amd.amc_p1, amd.amc_p2)

add_2_plus_1            = Perk(PERK_TYPE_ADD, 2, amd.amc_p1)
add_2_plus_1_push1      = Perk(PERK_TYPE_ADD, 2, amd.amc_plus_1_push1)
add_2_roll_plus_1       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_p1)
add_1_plus_3            = Perk(PERK_TYPE_ADD, 1, amd.amc_p3)

add_1_minus_2           = Perk(PERK_TYPE_ADD, 1, amd.amc_m2)
add_2_plus_2            = Perk(PERK_TYPE_ADD, 2, amd.amc_p2)

add_1_0_at              = Perk(PERK_TYPE_ADD, 1, amd.amc_0_at)
add_1_0_stun            = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_p1)
add_1_roll_at           = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_at)
add_1_roll_invis        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_invis)
add_1_plus_1_invis      = Perk(PERK_TYPE_ADD, 1, amd.amc_p1_invis)
add_1_roll_stun         = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_stun)
add_1_roll_disarm       = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_disarm)
add_1_roll_muddle       = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_muddle)
add_2_roll_muddle       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_muddle)
add_3_roll_muddle       = Perk(PERK_TYPE_ADD, 3, amd.amc_roll_muddle)
add_2_roll_poison       = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_poison)
add_3_roll_poison       = Perk(PERK_TYPE_ADD, 3, amd.amc_roll_poison)
add_2_roll_curse        = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_curse)
add_1_plus_1_immobilize = Perk(PERK_TYPE_ADD, 1, amd.amc_p1_immobilize)
add_1_plus_1_wound      = Perk(PERK_TYPE_ADD, 1, amd.amc_p1_wound)
add_2_roll_pierce3      = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_pierce_3)
add_2_roll_immobilize   = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_immobilize)

add_3_roll_push1        = Perk(PERK_TYPE_ADD, 3, amd.amc_roll_push1)
add_2_roll_push2        = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_push2)
add_3_roll_pull1        = Perk(PERK_TYPE_ADD, 3, amd.amc_roll_pull1)

add_2_roll_heal1        = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_heal1)

# elemental based
add_1_roll_air          = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_air)
add_2_roll_air          = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_air)
add_1_roll_dark         = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_dark)
add_1_roll_earth        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_earth)
add_2_roll_earth        = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_earth)
add_2_roll_fire         = Perk(PERK_TYPE_ADD, 2, amd.amc_roll_fire)
add_1_roll_light        = Perk(PERK_TYPE_ADD, 1, amd.amc_roll_light)

add_1_plus_1_curse      = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_1_curse)
add_1_plus_1_poison     = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_1_poison)
add_1_plus_2_muddle     = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_2_muddle)

add_1_0_fire            = Perk(PERK_TYPE_ADD, 1, amd.amc_0_fire)
add_1_0_ice             = Perk(PERK_TYPE_ADD, 1, amd.amc_0_ice)
add_1_0_air             = Perk(PERK_TYPE_ADD, 1, amd.amc_0_air)
add_1_0_earth           = Perk(PERK_TYPE_ADD, 1, amd.amc_0_earth)
add_3_0_fire            = Perk(PERK_TYPE_ADD, 3, amd.amc_0_fire)
add_3_0_ice             = Perk(PERK_TYPE_ADD, 3, amd.amc_0_ice)
add_3_0_air             = Perk(PERK_TYPE_ADD, 3, amd.amc_0_air)
add_3_0_earth           = Perk(PERK_TYPE_ADD, 3, amd.amc_0_earth)
add_1_plus_1_air        = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_1_air)
add_1_plus_2_fire       = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_2_fire)
add_1_plus_2_ice        = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_2_ice)

# class specific perks
tinkerer_perk_9         = Perk(PERK_TYPE_ADD, 1, amd.amc_p1h2)
brute_p1_shield1        = Perk(PERK_TYPE_ADD, 1, amd.amc_plus_1_shield1)
add_1_minus_1_dark      = Perk(PERK_TYPE_ADD, 1, amd.amc_minus_1_dark)
replace_minus_1_dark_with_plus_1_dark = Perk(PERK_TYPE_REPLACE, 1, amd.amc_minus_1_dark, amd.amc_plus_1_dark)

add_1_0_refresh_item    = Perk(PERK_TYPE_ADD, 1, amd.amc_0_ri)

brute_perk_deck = list([
    remove_2_minus_1,
    replace_minus_1_with_plus_1,
    add_2_plus_1, add_2_plus_1,
    add_1_plus_3,
    add_3_roll_push1, add_3_roll_push1,
    add_2_roll_pierce3,
    add_1_roll_stun, add_1_roll_stun,
    [add_1_roll_disarm, add_1_roll_muddle],
    add_1_roll_at, add_1_roll_at,
    brute_p1_shield1,
    ignore_scen_perk_plus_1
])

cragheart_perk_deck = list([
    remove_4_0,
    replace_minus_1_with_plus_1, replace_minus_1_with_plus_1, replace_minus_1_with_plus_1,
    [add_1_minus_2, add_2_plus_2],
    add_1_plus_1_immobilize, add_1_plus_1_immobilize,
    add_1_plus_2_muddle, add_1_plus_2_muddle,
    add_2_roll_push2,
    add_2_roll_earth, add_2_roll_earth,
    add_2_roll_air,
    ignore_item_perk,
    ignore_scen_perk
])

mindthief_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    remove_4_0,
    replace_2_plus_1_with_2_plus_2,
    replace_minus_2_with_0,
    add_1_plus_2_ice, add_1_plus_2_ice,
    add_2_roll_plus_1, add_2_roll_plus_1,
    add_3_roll_pull1,
    add_3_roll_muddle,
    add_2_roll_immobilize,
    add_1_roll_stun,
    [add_1_roll_disarm, add_1_roll_muddle],
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
    add_1_0_at,
    ignore_scen_perk
])

doomstalker_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    replace_2_0_with_2_plus_1, replace_2_0_with_2_plus_1, replace_2_0_with_2_plus_1,
    add_2_roll_plus_1, add_2_roll_plus_1,
    add_1_plus_2_muddle,
    add_1_plus_1_poison,
    add_1_plus_1_wound,
    add_1_plus_1_immobilize,
    add_1_0_stun,
    add_1_roll_at, add_1_roll_at,
    ignore_scen_perk
])

quartermaster_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    remove_4_0,
    replace_0_with_plus_2, replace_0_with_plus_2,
    add_2_roll_plus_1, add_2_roll_plus_1,
    add_3_roll_muddle,
    add_2_roll_pierce3,
    add_1_roll_stun,
    add_1_roll_at,
    add_1_0_refresh_item, add_1_0_refresh_item, add_1_0_refresh_item,
    ignore_item_perk_add_2_plus_1
])

elementalist_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    replace_minus_1_with_plus_1,
    replace_0_with_plus_2, replace_0_with_plus_2,
    add_3_0_fire,
    add_3_0_ice,
    add_3_0_air,
    add_3_0_earth,
    [remove_2_0, add_1_0_fire, add_1_0_earth],
    [remove_2_0, add_1_0_ice, add_1_0_air],
    add_2_plus_1_push1,
    add_1_plus_1_wound,
    add_1_0_stun,
    add_1_0_at
])

plagueherald_perk_deck = list([
    replace_minus_2_with_0,
    replace_minus_1_with_plus_1, replace_minus_1_with_plus_1,
    replace_0_with_plus_2, replace_0_with_plus_2,
    add_2_plus_1,
    add_1_plus_1_air, add_1_plus_1_air, add_1_plus_1_air,
    add_3_roll_poison,
    add_2_roll_curse,
    add_2_roll_immobilize,
    add_1_roll_stun, add_1_roll_stun,
    ignore_scen_perk_plus_1
])

nightshroud_perk_deck = list([
    remove_2_minus_1, remove_2_minus_1,
    remove_4_0,
    add_1_minus_1_dark, add_1_minus_1_dark,
    replace_minus_1_dark_with_plus_1_dark, replace_minus_1_dark_with_plus_1_dark,
    add_1_plus_1_invis, add_1_plus_1_invis,
    add_3_roll_muddle, add_3_roll_muddle,
    add_2_roll_heal1,
    add_2_roll_curse,
    add_1_roll_at,
    ignore_scen_perk_2_plus_1
])

beasttyrant_perk_deck = list([
    remove_2_minus_1,
    replace_minus_1_with_plus_1, replace_minus_1_with_plus_1, replace_minus_1_with_plus_1,
    replace_0_with_plus_2, replace_0_with_plus_2,
    add_1_plus_1_wound, add_1_plus_1_wound,
    add_1_plus_1_immobilize, add_1_plus_1_immobilize,
    add_2_roll_heal1, add_2_roll_heal1, add_2_roll_heal1,
    add_2_roll_earth,
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
    elif class_type == "doomstalker":
        return doomstalker_perk_deck
    elif class_type == "quartermaster":
        return quartermaster_perk_deck
    elif class_type == "elementalist":
        return elementalist_perk_deck
    elif class_type == "plagueherald":
        return plagueherald_perk_deck
    elif class_type == "nightshroud":
        return nightshroud_perk_deck 
    elif class_type == "beasttyrant":
        return beasttyrant_perk_deck
    else:
        raise Exception("[getPerkSelection]", "UNKNOWN CLASS TYPE")

if __name__ == "__main__":
    print('\nTinkerer')
    for perk in tinkerer_perk_deck:
        print(perk)

    print('\nScoundrel')
    for perk in scoundrel_perk_deck:
        print(perk)

    print('\nSpellweaver')
    for perk in spellweaver_perk_deck:
        print(perk)

    print('\nCragheart')
    for perk in cragheart_perk_deck:
        print(perk)

    print('\nBrute')
    for perk in brute_perk_deck:
        print(perk)
        
    print('\nMindthief')
    for perk in mindthief_perk_deck:
        print(perk)
        
    print('\nDoomstalker')
    for perk in doomstalker_perk_deck:
        print(perk)
        
    print('\nQuartermaster')
    for perk in quartermaster_perk_deck:
        print(perk)
    
    print('\nElementalist')
    for perk in elementalist_perk_deck:
        print(perk)
    
    print('\nPlagueherald')
    for perk in plagueherald_perk_deck:
        print(perk)
    
    print('\nNightshroud')
    for perk in nightshroud_perk_deck:
        print(perk)

    print('\nBeast Tyrant')
    for perk in beasttyrant_perk_deck:
        print(perk)
