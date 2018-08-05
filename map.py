"""
"""

import global_vars as gv
import room
import npc

class Map():
    def __init__(self, name, num):
        self.scen_name       = name
        self.scen_number     = num
        self.rooms           = dict()
        self.room_connectors = list()

    def __repr__(self):
        ret  = "Name: %s\n" % (self.scen_name)
        ret += "Comprised of %d rooms:\n  " % (len(self.rooms))
        for room in self.rooms:
            ret += "%s " % (room)
        return ret

    def getRoomByName(self, name):
        if name in self.rooms:
            return self.rooms[name]
        return None

    def addRooms(self, rList):
        assert len(self.rooms) == 0
        for room in rList:
            self.rooms[room.getName()] = room

    def connectRooms(self, r1, r1_conn, r2, r2_conn, row, col, connType=room.DOOR_TYPE_CLOSED):
        print("Connection Room Creation")
        connTile = room.GloomhavenTile(r1.getName()+'_'+r2.getName()+':%d,%d' % (row, col))
        connTile.setDoorType(connType)

        # assert we are connecting two rooms of same orientation
        assert r1.getOrientation() == r2.getOrientation()
        # assert we have all 6 edges for each room's connection array
        assert len(r1_conn) == 6 and len(r2_conn) == 6

        # make our room 1 edges
        for side, coords in enumerate(r1_conn):
            if coords:
                connTile.addNeighbor(side, r1.getTile(coords[0], coords[1]))

        # make our room 2 edges
        for side, coords in enumerate(r2_conn):
            if coords:
                connTile.addNeighbor(side, r2.getTile(coords[0], coords[1]))

        self.room_connectors.append(connTile)
        return connTile

    def mapCoordinates(self, start_room, r, c, roomRotations):
        start_room = self.getRoomByName(start_room)
        if start_room:
            curr_tile = start_room.getTile(0,0)
            curr_orientation = start_room.getOrientation()
            assert curr_tile is not None

            r = 0
            c = 0
            self.setMapCoordinates(curr_tile, r, c, curr_orientation, roomRotations)
        else:
            raise Exception("mapCoordinates Exception","'%s' room not found" % start_room)

    def setMapCoordinates(self, curr_tile, r, c, orientation, roomRots):
        while curr_tile:
            curr_tile.setMapLocation(gv.Location(r,c), roomRots)
            rotate = False
            roomName = curr_tile.unique_id.split(':')[0]
            if roomName in roomRots and (curr_tile.row_id, curr_tile.col_id):
                rotate = True
            if orientation == room.ORIENT_POINTY:
                for side_num in range(6):
                    neigh = curr_tile.getNeighbor(side_num)
                    if neigh and neigh.getMapLocation() == None:
                        offset = room.POINTY_EDGES[side_num]
                        if rotate:
                            offset = gv.rotateLocationLeft(offset, roomRots[roomName])
                        self.setMapCoordinates(neigh, r+offset[0], c+offset[1], orientation, roomRots)
            elif orientation == room.ORIENT_FLAT:
                for side_num in range(6):
                    neigh = curr_tile.getNeighbor(side_num)
                    if neigh and neigh.getMapLocation() == None:
                        offset = room.FLAT_EDGES[side_num]
                        if rotate:
                            offset = gv.rotateLocationLeft(offset, roomRots[roomName])
                        self.setMapCoordinates(neigh, r+offset[0], c+offset[1], orientaiton, roomRots)
            else:
                raise Exception("setMapCoordinates", "unknown orientation: %d" % orientation)
                curr_tile = None
            curr_tile = None

    def getTileByMapCoordinates(self, loc):
        for room in self.rooms:
            searchTile = self.getRoomByName(room).getTileByMapCoordinates(loc)
            if searchTile:
                return searchTile
        for tile in self.room_connectors:
            if tile.getMapLocation() == loc:
                return tile

        return None

# PathFinding
import collections
class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


def breadth_first_search(graph, start, goal):
    # assert our locations exist
    assert graph.getTileByMapCoordinates(start)
    assert graph.getTileByMapCoordinates(goal)

    frontier = Queue()

    start_tile = graph.getTileByMapCoordinates(start)
    goal_tile = graph.getTileByMapCoordinates(goal)
    frontier.put(start_tile)
    came_from = {}
    came_from[start] = None

    while not frontier.empty():
        current_tile = frontier.get()

        if current_tile == goal_tile:
            break

        for next in current_tile.getMapNeighbors():
            next_tile = graph.getTileByMapCoordinates(next)
            if next_tile and next not in came_from and next_tile.isPassable():
                frontier.put(next_tile)
                came_from[next] = current_tile.getMapLocation()

    #return came_from
    current = goal
    path = []
    while current != start:
       path.append(current)
       current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path


if __name__ == "__main__":
    # create map
    m = Map("Black Barrow", 1)

    # add rooms
    m.addRooms([room.G1b, room.I1b, room.L1a])
    print(m)

    # connect rooms
    cTile = m.connectRooms(room.L1a, [(3,1), (4,0), None, None, None, (2,0)],
                           room.G1b, [None, None, (0,0), (1,1), (2,0), None],
                           row=3, col=-1)
    #cTile.printTile()

    cTile = m.connectRooms(room.G1b, [None, (0,8), (0,6), None, None, None],
                           room.I1b, [None, (0,6), (0,4), None, None, None],
                           row=-1, col=7)

    # create objects
    table_1 = room.GloomhavenObject("Table", room.OBJ_OBSTACLE, [(1,1),(1,3)])
    table_2 = room.GloomhavenObject("Table", room.OBJ_OBSTACLE, [(1,7),(1,9)])
    room.I1b.addObject(table_1)
    room.I1b.addObject(table_2)
    
    # create traps
    trap_1 = room.GloomhavenObject("Damage_Trap", room.OBJ_TRAP, [(0,6),(0,8)])

    # create treasures
    treasure = room.GloomhavenObject("Treasure_07", room.OBJ_TREASURE,[(4,10)])
    room.I1b.addObject(treasure)

    # create coins
    coin = room.GloomhavenObject("Coin", room.OBJ_COIN, [(2,0), (3,1), (4,0), (2,10), (3,9)])
    room.I1b.addObject(coin)
    print(table_1)

    # set map coordinates for all tiles
    m.mapCoordinates('L1a', 0, 0, {'G1b':3, 'I1b':0})

    # NPCs
    bg = gv.monsterDataJson["Bandit Guard"]
    bandit_guard        = npc.NPC("Bandit Guard", bg["DeckType"])
    bandit_guard_elite  = npc.NPC("Bandit Guard", bg["DeckType"], elite=True)

    ba = gv.monsterDataJson["Bandit Archer"]
    bandit_archer       = npc.NPC("Bandit Archer", ba["DeckType"])
    bandit_archer_elite = npc.NPC("Bandit Archer", ba["DeckType"], elite=True)

    #lb = gv.monsterDataJson["Living Bones"]
    #living_bones        = npc.NPC("Living Bones", lb["DeckType"])

    parents = breadth_first_search(m, gv.Location(2, 8), gv.Location(10, -4))
    print(parents)
