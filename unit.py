'''
'''

class Unit():
    def __init__(self, id, name, elite=False, spawn=False):
        self.id     = id
        self.name   = name
        self.elite  = elite
        self.spawn  = spawn

    def isElite(self):
        return self.elite

    def isSpawn(self):
        return self.spawn
        
    def __repr__(self):
        str  = "[Unit: %d] %s\n" % (self.id, self.name)
        return str

if __name__ == "__main__":
    un = Unit(0, "Skeleton Archer")
    print(un)