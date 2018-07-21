'''
'''

_effects = ['Disarm', 'Immobolize', 'Invisibility', 'Muddle', 'Poison', 'Strengthen', 'Stun', 'Wound']

def initEffects():
    ret = {}
    for eff in _effects:
        ret[eff.lower()] = False
    return ret

def setEffect(effList, key, value):
    effList[key.lower()] = value
