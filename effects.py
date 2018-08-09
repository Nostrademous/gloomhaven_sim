'''
'''

_all_effects = ['Disarm', 'Immobilize', 'Invisibility', 'Muddle', 'Poison', 'Strengthen', 'Stun', 'Wound']
_one_turn_effects = ['Disarm', 'Immobilize', 'Invisibility', 'Muddle', 'Strengthen', 'Stun']

def initEffects():
    ret = {}
    for eff in _all_effects:
        ret[eff.lower()] = False
    return ret

def setEffect(effList, key, value=True):
    effList[key.lower()] = True

def hasEffect(effList, key):
    return effList[key.lower()]

def removeEffect(effList, key):
    effList[key.lower()] = False

def removeOneTurnEffects(effList):
    for eff in _one_turn_effects:
        removeEffect(effList, eff)
