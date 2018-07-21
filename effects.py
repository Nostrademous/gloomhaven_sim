'''
'''

_effects = ['Disarm', 'Immobolize', 'Muddle', 'Poison', 'Stun', 'Wound']

def initEffects():
    ret = {}
    for eff in _effects:
        ret[eff] = False
    return ret

