'''
'''

class AbilityCard():
    def __init__(self, id, name, level, initiative):
        self.id         = id
        self.name       = name
        self.level      = level
        self.initiative = initiative
    
    def __repr__(self):
        return "[%d] %s\n\tLevel: %d\n\tInitiative: %d\n" % (self.id, self.name, self.level, self.initiative)

if __name__ == "__main__":
    import global_vars as gv
    gv.init()
    
    for ability in gv.abilityDataJson.keys():
        ab = gv.abilityDataJson[ability]
        card = AbilityCard(int(ability), ab['Name'], ab['Level'], ab['Initiative'])
        print(card)