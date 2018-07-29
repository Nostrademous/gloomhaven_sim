'''
'''

from utils import strJson, pickRandom
import global_vars as gv

_action_types = {
    "Move_AdjEffect": ["Move", "AdjEffect"],
    "RangedHeal": ["Heal", "Range"],
    "Summon": ["SummonData"],
    "Special": ["UniqueID", "Text"]
}

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

    def getInitiative(self):
        return self.initiative

    def __repr__(self):
        ret  = "[%d] %s\nLevel: %d\nInitiative: %d\n" % (self.id, self.name, self.level, self.initiative)
        ret += "Top:\n%s\n" % (strJson(self.top))
        ret += "Bot:\n%s\n" % (strJson(self.bottom))
        return ret

    def __str__(self):
        return self.__repr__()

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
