'''
'''

from utils import pickRandom

class AttackModifierCard():
    def __init__(self, name, adjValue=0, crit=False, miss=False, reshuffle=False,
                 curse=False, bless=False, rolling=False, effect=None, effectValue=0,
                 invokeElement=None, heal=False, healAmount=0, addTarget=False):
        self.name       = name
        self.adjValue   = adjValue
        self.crit       = crit
        self.miss       = miss
        self.reshuffle  = reshuffle
        self.curse      = curse
        self.bless      = bless
        self.rolling    = rolling
        # element invocation cards
        self.invoke     = invokeElement
        # effect cards
        self.effect     = effect
        self.effectValue= effectValue
        # heal cards
        self.heal       = heal
        self.healAmount = healAmount
        # extra target cards
        self.addTarget  = addTarget

    def isCrit(self):
        return self.crit

    def isMiss(self):
        return self.miss

    def isCurse(self):
        return self.curse

    def isBlessing(self):
        return self.bless

    def isRolling(self):
        return self.rolling

    def isReshuffle(self):
        return self.reshuffle

    def __repr__(self):
        ret = ''
        if self.rolling:
            if self.name != '':
                ret += 'rolling %s' % self.name
            else:
                ret += 'rolling'
        else:
            ret += '%s' % self.name
        if self.bless:
            ret += ' BLESS'
        if self.curse:
            ret += ' CURSE'
        if self.invoke:
            ret += ' invoke %s' % (self.invoke.upper())
        if self.effect:
            ret += ' %s' % (self.effect.upper())
            if self.effectValue > 0:
                ret += '_%d' % (self.effectValue)
        if self.heal:
            ret += ' Heal %d' % (self.healAmount)
        if self.addTarget:
            ret += ' Add Target'
        return ret

amc_0   = AttackModifierCard('+0', 0)
amc_m1  = AttackModifierCard('-1', -1)
amc_p1  = AttackModifierCard('+1', 1)
amc_m2  = AttackModifierCard('-2', -2)
amc_p2  = AttackModifierCard('+2', 2)
amc_cr  = AttackModifierCard('x2', 0, crit=True, reshuffle=True)
amc_ms  = AttackModifierCard('0', 0, miss=True, reshuffle=True) 

amc_curse = AttackModifierCard('curse', 0, miss=True, curse=True)
amc_bless = AttackModifierCard('bless', 0, crit=True, bless=True)

# below are perk-specific cards that can be added via perks
amc_p3              = AttackModifierCard('+3', 3)
amc_p1h2            = AttackModifierCard('+1', 1, heal=True, healAmount=2)
amc_roll_air        = AttackModifierCard('', rolling=True, invokeElement='air')
amc_roll_dark       = AttackModifierCard('', rolling=True, invokeElement='dark')
amc_roll_earth      = AttackModifierCard('', rolling=True, invokeElement='earth')
amc_roll_fire       = AttackModifierCard('', rolling=True, invokeElement='fire')
amc_roll_light      = AttackModifierCard('', rolling=True, invokeElement='light')
amc_roll_invis      = AttackModifierCard('', rolling=True, effect='invisible')
amc_roll_muddle     = AttackModifierCard('', rolling=True, effect='muddle')
amc_roll_pierce_3   = AttackModifierCard('', rolling=True, effect='pierce', effectValue=3)
amc_roll_poison     = AttackModifierCard('', rolling=True, effect='poison')
amc_roll_stun       = AttackModifierCard('', rolling=True, effect='stun')
amc_0at             = AttackModifierCard('+0', addTarget=True)
amc_p1_wound        = AttackModifierCard('+1', effect='wound')
amc_p1_immobilize   = AttackModifierCard('+1', effect='immobilize')
amc_roll_p1         = AttackModifierCard('+1', rolling=True)
amc_plus_2_fire     = AttackModifierCard('+2', invokeElement='fire')
amc_plus_2_ice      = AttackModifierCard('+2', invokeElement='ice')
amc_plus_1_curse    = AttackModifierCard('+1', curse=True)
amc_0_stun          = AttackModifierCard('+0', effect='stun')

_start_deck = list([
    amc_0, amc_0, amc_0, amc_0, amc_0, amc_0, # 6 +0 cards
    amc_m1, amc_m1, amc_m1, amc_m1, amc_m1,   # 5 -1 cards
    amc_p1, amc_p1, amc_p1, amc_p1, amc_p1,   # 5 +1 cards
    amc_m2, amc_p2, amc_cr, amc_ms            # 4 others
])

_player_curse_deck = list([
    amc_curse, amc_curse, amc_curse, amc_curse, amc_curse,
    amc_curse, amc_curse, amc_curse, amc_curse, amc_curse
])

_bless_deck = list([
    amc_bless, amc_bless, amc_bless, amc_bless, amc_bless,
    amc_bless, amc_bless, amc_bless, amc_bless, amc_bless
])

_monster_curse_deck = list([
    amc_curse, amc_curse, amc_curse, amc_curse, amc_curse,
    amc_curse, amc_curse, amc_curse, amc_curse, amc_curse
])

class AttackModifierDeck():
    def __init__(self, isPlayer):
        self._deck = _start_deck
        self.play_deck = list(self._deck)
        self.reshuffle = False
        self.isPlayer = isPlayer

    def addCurse(self):
        print('Adding Curse')
        if self.isPlayer:
            if len(_player_curse_deck) > 0:
                curse = pickRandom(_player_curse_deck)
                _player_curse_deck.remove(curse)
            else:
                print('No more Player Curses Available, ignoring...')
                return
        else:
            if len(_monster_curse_deck) > 0:
                curse = pickRandom(_monster_curse_deck)
                _monster_curse_deck.remove(curse)
            else:
                print('No more Monster Curses Available, ignoring...')
                return
        self._deck.append(curse)
        self.play_deck.append(curse)

    def removeCurse(self, curse):
        #print('Removing Curse')
        self._deck.remove(curse)
        if self.isPlayer:
            _player_curse_deck.append(curse)
        else:
            _monster_curse_deck.append(curse)

    def addBlessing(self):
        print('Adding Blessing')
        if len(_bless_deck) > 0:
            bless = pickRandom(_bless_deck)
            _bless_deck.remove(bless)
            self._deck.append(bless)
            self.play_deck.append(bless)
        else:
            print('No more blessings available, ignoring...')

    def removeBlessing(self, bless):
        #print('Removing Blessing')
        self._deck.remove(bless)
        _bless_deck.append(bless)

    def pickCard(self, ret_draw=[]):
        card = pickRandom(self.play_deck)
        if card.isCurse():
            self.removeCurse(card)
        elif card.isBlessing():
            self.removeBlessing(card)
        if card.isReshuffle():
            self.reshuffle = True
        self.play_deck.remove(card)
        print(card)
        ret_draw.append(card)

        if card.isRolling():
            self.pickCard(ret_draw)
        return ret_draw

    def endTurn(self):
        print('End of turn')
        if self.reshuffle:
            print('Reshuffling Attack Modifier Deck')
            self.play_deck = list(self._deck)
        self.reshuffle = False

    def __repr__(self):
        return str(self.play_deck)

if __name__ == "__main__":
    deck = AttackModifierDeck(isPlayer=True)

    print(deck)
    for i in range(2):
        deck.pickCard()
    deck.endTurn()

    deck.addBlessing()
    deck.addCurse()

    print(deck)
    for i in range(3):
        deck.pickCard()
    deck.endTurn()
    print(deck)
    #print(_player_curse_deck)
    #print(_bless_deck)
