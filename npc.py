'''
'''

from unit import Unit

class NPC(Unit):
    def __init__(self, name, id=0, elite=False, spawn=False):
        super().__init__(name, id)
        self.elite  = elite
        self.spawn  = spawn

    def isElite(self):
        return self.elite

    def isSpawn(self):
        return self.spawn

if __name__ == "__main__":
    un = NPC("Skeleton Archer", 0)
    print(un)
