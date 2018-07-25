'''
'''

from utils import strJson

_ability_types = {
    "Move_AdjEffect": ["Move", "AdjEffect"],
    "Ranged_Heal": ["Heal", "Range"],
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

class AbilityCardDeck():
    def __init__(self, heroType, level=9):
        self._all_cards = loadAllHeroCards(heroType, level)
        self.selected_cards = list()
        self.active_cards   = list()
        self.lost_cards     = list()
        self.discard_cards  = list()

    def useCardTop(self, card):
        print("IMPLEMENT")
        self.selected_cards.remove(card)
        if card.top.has_key('Lasts'):
            self.active_cards.append(card)
        elif card.top.has_key('Lost'):
            self.lost_cards.append(card)
        else:
            self.discard_cards.append(card)

    def useCardBot(self, card):
        print("IMPLEMENT")
        self.selected_cards.remove(card)
        if card.bottom.has_key('Lasts'):
            self.active_cards.append(card)
        elif card.bottom.has_key('Lost'):
            self.lost_cards.append(card)
        else:
            self.discard_cards.append(card)

if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    tinkerer_cards = loadAllHeroCards("tinkerer", 9)
    for tc in tinkerer_cards:
        print(tc)