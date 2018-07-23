'''
'''

from utils import strJson

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

if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    for ability in gv.abilityDataJson.keys():
        ab = gv.abilityDataJson[ability]
        card = AbilityCard(int(ability), ab['Name'], ab['Level'], ab['Initiative'])
        card.addTop(ab['Top'])
        card.addBottom(ab['Bottom'])
        print(card)