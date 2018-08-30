'''
'''

from utils import strJson, pickRandom
import global_vars as gv

_action_types = {
    "Attack": ["AttackValue"],
    "Move": ["MoveValue"],
    "RangedAttack": ["AttackValue", "RangeValue"],
    "RangedHeal": ["HealValue", "RangeValue"],
    "CreateTrap": ["TrapDamage", "TrapLocation", "TrapEffect"],
    "SummonData": ["Name", "Health", "Move", "Attack", "Range"],
    "RangedLoot": ["RangeValue"],
    "AdjacentBuffAll": ["BuffType", "BuffValue", "Rounds"],
    "AdjacentHealAll": ["HealValue", "TargetType"],
    "AdjacentEffectOne": ["Effect"],
    "AdjacentEffectAll": ["Effect"],
    "AdjacentDamageAll": ["DamageValue", "TargetType"],
    "AdjacentAllySpecial": ["Special", "Rounds"],
    "SelfBuff": ["BuffType", "BuffValue", "Rounds"],
    "SelfDamage": ["DamageValue"],
    "MultiRoundBuff": ["BuffType", "BuffValue", "BuffCount"],
    "DiscardRecovery": ["NumCards", "Target"],
    "RangedDiscardRecovery": ["NumCards", "RangeValue"],
    "KillAdjacentEnemy": ["MaxType"],
    "AllSummonRangeBuff": ["BuffType", "BuffValue", "BuffControl", "RangeValue"],
    "VariableAttack": ["VariableType", "Scaling"],
    "VariableMove": ["VariableType", "Scaling"],
    "Special": ["UniqueID", "Text"]
}


def hasModifier(action):
    return 'Modifier' in action

def getModifier(action):
    return action.get('Modifier')

def hasEffect(action):
    return 'Effect' in action

def getEffect(action):
    return action.get('Effect')

def invokesElement(action):
    return action.get('ElementalInvoke')

def consumesElement(action):
    if 'ElementalBuff' in action:
        return action['ElementalBuff']['Element']
    return None

def isAoEAttack(action):
    return action.get('AttackValue') and action.get('AoEShape')

def maxAoETargets(action):
    assert isAoEAttack(action)
    cnt = sum(action.get('AoEShape'))
    if action.get('Type') == 'RangedAttack':
        cnt += 1
    return cnt

def isVariable(action):
    return action.get('Type')[:8] == 'Variable'

def isPlacedActive(section):
    return section.get('Lasts') == 'Infinite'

def isLost(section):
    return 'Lost' in section

def grantsXP(section):
    return 'XP' in section

def interpretAction(action):
    assert action.get('Type') in _action_types

    if isVariable(action):
        print("Variable on %s scaled 1:%d" % (action.get('VariableType'), action.get('Scaling')))
    if isAoEAttack(action):
        print("AoE Attack: %s, MaxTargets: %d" % (action.get('AoEShape'), maxAoETargets(action)))
    if hasModifier(action):
        print("Modifier: %s" % getModifier(action))
    if hasEffect(action):
        print("Effect: %s" % getEffect(action))
    invokedElement = invokesElement(action)
    if invokedElement:
        print("Invokes '%s'" % invokedElement)
   
    for reqField in _action_types[action['Type']]:
        print("%s: %s" % (reqField, action[reqField]))

def interpretCardSection(section):
    actions = section['Actions']
    if isLost(section):
        print("LOST ON USE")
    if grantsXP(section):
        print("GRANTS XP")
    if isPlacedActive(section):
        print("STAYS ACTIVE")
    for actionIndex in actions:
        action = actions[actionIndex]
        interpretAction(action)


class AbilityCard():
    def __init__(self, id, name, level, initiative):
        self.id         = id
        self.name       = name
        self.level      = level
        self.initiative = initiative
        self.top        = {}
        self.bottom     = {}

    def addTop(self, dictTop):
        self.top = dictTop

    def addBottom(self, dictBottom):
        self.bottom = dictBottom

    def getTop(self):
        return self.top

    def getBottom(self):
        return self.bottom

    # for use with DEFAULT TOP & BOTTOM actions
    def setInitiative(self, value):
        self.initiative = value

    def getInitiative(self):
        return self.initiative

    def __repr__(self):
        ret  = "[%d] %s\nLevel: %d\nInitiative: %d\n" % (self.id, self.name, self.level, self.initiative)
        ret += "Top:\n%s\n" % (strJson(self.top))
        ret += "Bot:\n%s\n" % (strJson(self.bottom))
        return ret

    def __str__(self):
        return self.__repr__()

DEFAULT = AbilityCard(0, "Default Top", 0, 100)
DEFAULT.addTop({"Actions": { "1": {"Type": "Attack", "Value": 2} } })
DEFAULT.addBottom({"Actions": { "1": {"Type": "Move", "Value": 2} } })

def loadAllHeroCards(heroType, level):
    card_list = list()
    for ability in gv.abilityDataJson.keys():
        ab = gv.abilityDataJson[ability]
        if ab['Class'].lower() == heroType.lower():
            if ab['Level'] <= level:
                card = AbilityCard(int(ability), ab['Name'], ab['Level'], ab['Initiative'])
                card.addTop(ab['Top'])
                card.addBottom(ab['Bottom'])
                card_list.append(card)
    return card_list

class HeroAbilityCardDeck():
    def __init__(self, heroType, level=9):
        self._all_cards = loadAllHeroCards(heroType, level)
        self.selected_cards = list()
        self.active_cards   = list()
        self.lost_cards     = list()
        self.discard_cards  = list()
        self.in_hand_cards  = list()

    def selectCardsFromFullDeck(self, maxNum):
        # TODO - random for now, but ultimately user/AI selected
        selection_deck = list(self._all_cards)
        for i in range(maxNum):
            card = pickRandom(selection_deck)
            if card:
                selection_deck.remove(card)
                self.selected_cards.append(card)
                if len(selection_deck) == 0:
                    print("[selectCardsFromFullDeck] :: Not enough cards")
                    break

    def selectRoundCards(self):
        self.in_hand_cards = list()
        # TODO - random for now, but ultimately user/AI selected
        for i in range(2):
            card = pickRandom(self.selected_cards)
            if card:
                self.selected_cards.remove(card)
                self.in_hand_cards.append(card)

        # Pick Top Card for Initiative
        # TODO - random for now, but ultimately user/AI selected
        return  pickRandom([0,1])

    def getNumRemainingCards(self):
        return len(self.selected_cards)

    def pickRandomDiscardedCardForLoss(self):
        return pickRandom(self.discard_cards)

    # specific to short-rest recover of random loss card
    def keepLossCardPickNewRandomDiscard(self, lossCard):
        self.dicard_cards.remove(lossCard)
        self.selected_cards.append(lossCard)
        return self.pickRandomDiscardedForLoss()

    def recoverDiscardedCards(self, lossCard=None):
        if lossCard is not None:
            self.dicard_cards.remove(lossCard)
            self.lost_cards.append(lossCard)
        self.selected_cards.extend(self.discard_cards)

    def useCardTop(self, card):
        self.selected_cards.remove(card)
        if card.top.has_key('Lasts'):
            self.active_cards.append(card)
        elif card.top.has_key('Lost'):
            self.lost_cards.append(card)
        else:
            self.discard_cards.append(card)
        return card.top

    def useCardBot(self, card):
        self.selected_cards.remove(card)
        if card.bottom.has_key('Lasts'):
            self.active_cards.append(card)
        elif card.bottom.has_key('Lost'):
            self.lost_cards.append(card)
        else:
            self.discard_cards.append(card)
        return card.bottom

    def __repr__(self):
        ret = ''
        for c in self.selected_cards:
            ret += str(c)
        return ret


class MonsterAbilityCardDeck():
    def __init__(self, monsterType):
        self.card_pool  = list()

if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    tinkerer_cards = loadAllHeroCards("tinkerer", 9)
    for tc in tinkerer_cards:
        print(tc)
        interpretCardSection(tc.getTop())
        interpretCardSection(tc.getBottom())

    brute_cards = loadAllHeroCards("brute", 9)
    for bc in brute_cards:
        print(bc)
        interpretCardSection(bc.getTop())
        interpretCardSection(bc.getBottom())
