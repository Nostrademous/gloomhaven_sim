"""
"""

import room

class Map():
    def __init__(self, name, num):
        self.scen_name       = name
        self.scen_number     = num
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
        connTile = room.GloomhavenTile(r1.getName()+'_'+r2.getName()+':%d,%d' % (r1_row, r1_col))
        connTile.setDoorType(connType)
        # assert we are connecting two rooms of same orientation
        assert r1.getOrientation() == r2.getOrientation()
        if r1.getOrientation() == room.ORIENT_FLAT:
            print("CHECK FLAT CONNECTION")
            poss_neighbors = [(-2,0), (-1,1), (-1,-1), (1,1), (1,-1), (2,0)]
            for poss_conn in poss_neighbors:
                poss_row = r1_row + poss_conn[0]
                poss_col = r1_col + poss_conn[1]
                candidate = r1.getTile(poss_row, poss_col)
                if candidate != None:
                    candidate.addNeighbor(candidate.findNeighborEdgeId(connTile, r1.getOrientation()), connTile)
        elif r1.getOrientation() == room.ORIENT_POINTY:
            poss_neighbors = [(0,-2), (-1,1), (-1,-1), (1,1), (1,-1), (0,2)]
            for poss_conn in poss_neighbors:
                poss_row = r1_row + poss_conn[0]
                poss_col = r1_col + poss_conn[1]
                candidate = r1.getTile(poss_row, poss_col)
                if candidate != None:
                    candidate.addNeighbor(candidate.findNeighborEdgeId(connTile, r1.getOrientation()), connTile)

if __name__ == "__main__":
    # create map
    m = Map("Black Barrow", 1)

    # add rooms
    m.addRooms([room.G1b, room.I1b, room.L1a])
    print(m)

    # connect rooms
    m.connectRooms(room.L1a, 3, -1, room.G1b)
    m.connectRooms(room.G1b, 1, -1, room.L1a)
    m.connectRooms(room.G1b, -1, 7, room.I1b)
    m.connectRooms(room.I1b, -1, 5, room.G1b)
    room.G1b.printRoom()

    # create objects
    table_1 = room.GloomhavenObject("Table", room.OBJ_OBSTACLE,[(1,1),(1,3)])
    table_2 = room.GloomhavenObject("Table", room.OBJ_OBSTACLE,[(1,7),(1,9)])
    room.I1b.addObstacle(table_1)
    room.I1b.addObstacle(table_2)
    print(table_1)
