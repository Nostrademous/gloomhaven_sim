'''
'''

import copy
from utils import pickRandom

class AttackModifierCard():
    def __init__(self, name, adjValue=0, crit=False, miss=False, reshuffle=False,
                 curse=False, bless=False, rolling=False, effect=None, effectValue=0,
                 invokeElement=None, heal=False, healAmount=0, addTarget=False,
                 pullValue=0, pushValue=0, refreshItem=False, regen=False,
                 affectAllyCard=False):
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
        self.regen      = regen
        # extra target cards
        self.addTarget  = addTarget

        # push/pull vards
        self.pushValue  = pushValue
        self.pullValue  = pullValue
        
        # item related
        self.refreshItem = refreshItem

        # affect ally cards
        self.affectAllyCard = affectAllyCard

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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

    def isPush(self):
        return self.pushValue > 0

    def isPull(self):
        return self.pullValue > 0

    def isRefreshItem(self):
        return self.refreshItem

    def isAffectAllyCard(self):
        return self.affectAllyCard

    def calcDmg(self, value=1):
        if self.isMiss() or self.isCurse(): return 0
        if self.isCrit() or self.isBlessing(): return 2 * value
        return max(value + self.adjValue, 0)

    def __repr__(self):
        ret = ''
        if self.rolling:
            if self.name != '':
                ret += 'rolling %s' % self.name
            else:
                ret += 'rolling'
        else:
            ret += '%s' % self.name
        if self.isPush():
            ret += ' PUSH %d' % (self.pushValue)
        if self.isPull():
            ret += ' PULL %d' % (self.pullValue)
        if self.isRefreshItem():
            ret += ' REFRESH ITEM'
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
        if self.regen:
            ret += ' REGENERATE'
        if self.addTarget:
            ret += ' Add Target'
        if self.isAffectAllyCard():
            ret += ' (Affect any Ally card)'
        return ret

amc_0   = AttackModifierCard('+0', 0)
amc_m1  = AttackModifierCard('-1', -1)
amc_p1  = AttackModifierCard('+1', 1)
amc_m2  = AttackModifierCard('-2', -2)
amc_p2  = AttackModifierCard('+2', 2)
amc_p3  = AttackModifierCard('+3', 3)
amc_p4  = AttackModifierCard('+4', 4)
amc_cr  = AttackModifierCard('x2', 0, crit=True, reshuffle=True)
amc_ms  = AttackModifierCard('0', 0, miss=True, reshuffle=True)

amc_curse = AttackModifierCard('curse', 0, miss=True, curse=True)
amc_bless = AttackModifierCard('bless', 0, crit=True, bless=True)

# below are perk-specific cards that can be added via perks
amc_p1h2            = AttackModifierCard('+1', 1, heal=True, healAmount=2)
amc_roll_air        = AttackModifierCard('', rolling=True, invokeElement='air')
amc_roll_dark       = AttackModifierCard('', rolling=True, invokeElement='dark')
amc_roll_earth      = AttackModifierCard('', rolling=True, invokeElement='earth')
amc_roll_fire       = AttackModifierCard('', rolling=True, invokeElement='fire')
amc_roll_light      = AttackModifierCard('', rolling=True, invokeElement='light')
amc_roll_invis      = AttackModifierCard('', rolling=True, effect='invisible')
amc_roll_disarm     = AttackModifierCard('', rolling=True, effect='disarm')
amc_roll_immobilize = AttackModifierCard('', rolling=True, effect='immobilize')
amc_roll_muddle     = AttackModifierCard('', rolling=True, effect='muddle')
amc_roll_pierce_3   = AttackModifierCard('', rolling=True, effect='pierce', effectValue=3)
amc_roll_poison     = AttackModifierCard('', rolling=True, effect='poison')
amc_roll_wound      = AttackModifierCard('', rolling=True, effect='wound')
amc_roll_stun       = AttackModifierCard('', rolling=True, effect='stun')
amc_roll_at         = AttackModifierCard('', rolling=True, addTarget=True)
amc_roll_curse      = AttackModifierCard('', rolling=True, curse=True)
amc_0_at            = AttackModifierCard('+0', addTarget=True)
amc_0_fire          = AttackModifierCard('+0', invokeElement='fire')
amc_0_ice           = AttackModifierCard('+0', invokeElement='ice')
amc_0_air           = AttackModifierCard('+0', invokeElement='air')
amc_0_earth         = AttackModifierCard('+0', invokeElement='earth')
amc_p1_disarm       = AttackModifierCard('+1', effect='disarm')
amc_p1_wound        = AttackModifierCard('+1', effect='wound')
amc_p2_wound        = AttackModifierCard('+2', effect='wound')
amc_p1_immobilize   = AttackModifierCard('+1', effect='immobilize')
amc_roll_p1         = AttackModifierCard('+1', rolling=True)
amc_roll_p1_disarm  = AttackModifierCard('+1', rolling=True, effect='disarm')
amc_roll_p2         = AttackModifierCard('+2', rolling=True)
amc_plus_1_air      = AttackModifierCard('+1', invokeElement='air')
amc_plus_2_fire     = AttackModifierCard('+2', invokeElement='fire')
amc_plus_2_ice      = AttackModifierCard('+2', invokeElement='ice')
amc_plus_1_curse    = AttackModifierCard('+1', curse=True)
amc_plus_2_curse    = AttackModifierCard('+2', curse=True)
amc_plus_1_poison   = AttackModifierCard('+1', effect='poison')
amc_plus_2_poison   = AttackModifierCard('+2', effect='poison')
amc_plus_2_muddle   = AttackModifierCard('+2', effect='muddle')
amc_plus_3_muddle   = AttackModifierCard('+3', effect='muddle')
amc_plus_3_shield1  = AttackModifierCard('+3', effect='shield', effectValue=1)
amc_0_stun          = AttackModifierCard('+0', effect='stun')
amc_plus_1_shield1  = AttackModifierCard('+1', effect='shield', effectValue=1)
amc_plus_1_shield1_ally = AttackModifierCard('+1', effect='shield', effectValue=1, affectAllyCard=True)
amc_plus_1_push1    = AttackModifierCard('+1', pushValue=1)
amc_roll_push1      = AttackModifierCard('', rolling=True, pushValue=1)
amc_roll_pull1      = AttackModifierCard('', rolling=True, pullValue=1)
amc_roll_push2      = AttackModifierCard('', rolling=True, pushValue=2)
amc_roll_heal1      = AttackModifierCard('', rolling=True, heal=True, healAmount=1)
amc_roll_heal3      = AttackModifierCard('', rolling=True, heal=True, healAmount=3)
amc_roll_shield1    = AttackModifierCard('', rolling=True, effect='shield', effectValue=1)

amc_minus_1_dark    = AttackModifierCard('-1', invokeElement='dark')
amc_plus_1_dark     = AttackModifierCard('+1', invokeElement='dark')
amc_plus_2_dark     = AttackModifierCard('+2', invokeElement='dark')
amc_plus_2_light    = AttackModifierCard('+2', invokeElement='light')
amc_p1_invis        = AttackModifierCard('+1', effect='invisible')
amc_p1_heal2_ally   = AttackModifierCard('+1', heal=True, healAmount=2, affectAllyCard=True)
amc_p2_regen        = AttackModifierCard('+2', regen=True)

amc_0_ri            = AttackModifierCard('+0', refreshItem=True)

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
        self._deck = copy.deepcopy(_start_deck)
        self.play_deck = copy.deepcopy(_start_deck)
        self.reshuffle = False
        self.isPlayer = isPlayer

    def addCards(self, cards):
        self._deck.extend(cards)
        self.play_deck = copy.deepcopy(self._deck)

    def removeCards(self, cards):
        for card in cards:
            self._deck.remove(card)
        self.play_deck = copy.deepcopy(self._deck)

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
        print('Removing Curse')
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
        print('Removing Blessing')
        self._deck.remove(bless)
        _bless_deck.append(bless)

    def pickCard(self, ret_draw=[]):
        card = pickRandom(self.play_deck)
        
        # in the event that we are drawing multiple cards for one attack round (i.e., AoE)
        # it is possible that we 'exhaust' the deck before a reshuffle card is drawn
        # in that event, we are to reshuffle immediately
        if not card:
            print("AMD Exhausted - reshuffling")
            self.play_deck = copy.deepcopy(self._deck)
            for c in ret_draw:
                self.play_deck.remove(c)
            card = pickRandom(self.play_deck)

        if card.isCurse():
            self.removeCurse(card)
        elif card.isBlessing():
            self.removeBlessing(card)
        if card.isReshuffle():
            self.reshuffle = True
        self.play_deck.remove(card)
        #print(card)
        ret_draw.append(card)

        if card.isRolling():
            #print("ROLLING")
            self.pickCard(ret_draw)
            
        #print("Size Remaining: %d :: %s :: %s" % (len(self.play_deck), card, self.play_deck))
        return ret_draw

    def endTurn(self):
        #print('End of turn')
        if self.reshuffle:
            self.play_deck = copy.deepcopy(self._deck)
            #print('Reshuffling Attack Modifier Deck :: %d' % (len(self.play_deck)))
        self.reshuffle = False

    def __repr__(self):
        return str(self.play_deck)

if __name__ == "__main__":
    deck = AttackModifierDeck(isPlayer=True)

    '''
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
    '''

    from statistics import mean, variance, stdev
    d0 = deck
    d1 = AttackModifierDeck(isPlayer=True)
    d2 = AttackModifierDeck(isPlayer=True)
    d3 = AttackModifierDeck(isPlayer=True)
    d4 = AttackModifierDeck(isPlayer=True)
    d5 = AttackModifierDeck(isPlayer=True)
    d6 = AttackModifierDeck(isPlayer=True)
    d7 = AttackModifierDeck(isPlayer=True)

    # test 1 - remove one minus 2, add one plus 0
    d1.removeCards([amc_m2])
    d1.addCards([amc_0])

    # test 2 - remove two minus 1 cards
    d2.removeCards([amc_m1, amc_m1])

    # test 3 - add one +3 card (Tinkerer)
    d3.addCards([amc_p3])

    # test 4 - add two +1 cards
    d4.addCards([amc_p1, amc_p1])

    # test 5 - Remove for +0 cards
    d5.removeCards([amc_0, amc_0, amc_0, amc_0])

    # test 6 - add two rolling +1 cards
    d6.addCards([amc_roll_p1, amc_roll_p1])

    # test 7 - come test 1 and test 2 twice and test 5
    d7.removeCards([amc_m2])
    d7.addCards([amc_0])
    d7.removeCards([amc_m1, amc_m1])
    d7.removeCards([amc_m1, amc_m1])
    d7.removeCards([amc_0, amc_0, amc_0, amc_0])


    test_decks = [d0, d1, d2, d3, d4, d5, d6, d7]
    score = [[] for i in test_decks]
    test_range = 20000.
    num_picks_per_round = 1 # set this to large values to simulate AoE attacks
    ab_dmg = 1 # set this to the Ability Card's base Attack Damage Value you want simulated

    for i in range(int(test_range)):
        for indx, dk in enumerate(test_decks):
            ret = []
            for cnt in range(num_picks_per_round):
                ret = dk.pickCard(ret)
            dk.endTurn()
            score[indx].extend([i.calcDmg(ab_dmg) for i in ret])


    for indx, dk in enumerate(test_decks):
        m = mean(score[indx])
        v = stdev(score[indx], m)
        print("Deck %d AvgDmg when doing %d dmg Attack: %.4f, StdDev: %.4f, Spread: %.4f to %.4f" % (indx, ab_dmg, m, v, m-v, m+v))
