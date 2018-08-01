"""
"""

import room

class Map():
    def __init__(self, name):
        self.scen_name  = name
        self.rooms      = list()

    def __repr__(self):
        ret  = "Name: %s\n" % (self.scen_name)
        ret += "Comprised of %d rooms:\n  " % (len(self.rooms))
        for room in self.rooms:
            ret += "%s " % (room.getName())
        return ret

    def addRooms(self, rList):
        assert len(self.rooms) == 0
        self.rooms.extend(rList)

if __name__ == "__main__":
    m = Map("Black Barrows")
    m.addRooms([room.G1b, room.I1b, room.L1a])
    print(m)