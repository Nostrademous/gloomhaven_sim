"""
"""

import room

class Map():
    def __init__(self, name):
        self.scen_name       = name
        self.rooms           = dict()
        self.room_connectors = dict()

    def __repr__(self):
        ret  = "Name: %s\n" % (self.scen_name)
        ret += "Comprised of %d rooms:\n  " % (len(self.rooms))
        for room in self.rooms:
            ret += "%s " % (room)
        return ret

    def addRooms(self, rList):
        assert len(self.rooms) == 0
        for room in rList:
            self.rooms[room.getName()] = room

    def connectRooms(self, r1, r1_row, r1_col, r2, connType=room.DOOR_TYPE_CLOSED):
        print("[connectRooms] - IMPLEMENT")
        connTile = room.GloomhavenTile(r1.getName()+'_'+r2.getName()+':%d,%d' % (r1_row, r1_col))
        connTile.setDoorType(connType)
        # assert we are connecting two rooms of same orientation
        assert r1.getOrientation() == r2.getOrientation()
        if r1.getOrientation() == room.ORIENT_FLAT:
            print("IMPLEMENT FLAT CONNECTION")
            poss_neighbors = [(-2,0), (-1,1), (-1,-1), (1,1), (1,-1), (2,0)]
        elif r1.getOrientation() == room.ORIENT_POINTY:
            print("IMPLEMENT POINTY CONNECTON")
            poss_neighbors = [(0,-2), (-1,1), (-1,-1), (1,1), (1,-1), (0,2)]
            for poss_conn in poss_neighbors:
                poss_row = r1_row + poss_conn[0]
                poss_col = r1_col + poss_conn[1]
                candidate = r1.getTile(poss_row, poss_col)
                if candidate != None:
                    candidate.addNeighbor(candidate.findNeighborEdgeId(connTile, r1.getOrientation()), connTile)

if __name__ == "__main__":
    m = Map("Black Barrows")
    m.addRooms([room.G1b, room.I1b, room.L1a])
    print(m)
    m.connectRooms(room.L1a, 3, -1, room.G1b)
    room.L1a.printRoom()
    m.connectRooms(room.G1b, 1, -1, room.L1a)
    room.G1b.printRoom()
