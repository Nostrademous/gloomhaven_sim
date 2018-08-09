"""
"""

import global_vars as gv
import room
import npc

class Map():
    def __init__(self, name, num, scenDiff):
        self.scen_name       = name
        self.scen_number     = num
        self.difficulty      = scenDiff
        self.rooms           = dict()
        self.room_connectors = list()

        # scenario specific
        self.start_room      = None

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

    def setStartingRoom(self, name):
        assert name in self.rooms
        self.start_room = self.getRoomByName(name)
        self.start_room.setOpen()

    def spawnStartingRoom(self):
        assert self.start_room
        self.start_room.spawnNPCs()

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
import heapq
class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(graph, start, goal, hasJump=False, hasFlying=False):
    # assert our locations exist
    assert graph.getTileByMapCoordinates(start)
    assert graph.getTileByMapCoordinates(goal)

    frontier = PriorityQueue()

    start_tile = graph.getTileByMapCoordinates(start)
    goal_tile = graph.getTileByMapCoordinates(goal)
    frontier.put(start_tile, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current_tile = frontier.get()

        if current_tile == goal_tile:
            break

        current = current_tile.getMapLocation()
        for next in current_tile.getMapNeighbors():
            next_tile = graph.getTileByMapCoordinates(next)
            if next_tile and next_tile.isPassable():
                new_cost = cost_so_far[current] + next_tile.costToEnter(graph.difficulty, hasJump, hasFlying)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next_tile, priority)
                    came_from[next] = current

    #return came_from
    current = goal
    path = []
    while current != start:
       path.append(current)
       current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path, cost_so_far[goal]


def scenario_1(numPlayers):
    gv.setNumPlayersInScenario(numPlayers)

    # create map
    m = Map("Black Barrow", 1, scenDiff=1)

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
    trap_1 = room.GloomhavenObject("Damage_Trap", room.OBJ_TRAP, [(0,6)])
    trap_2 = room.GloomhavenObject("Damage_Trap", room.OBJ_TRAP, [(0,8)])
    room.G1b.addObject(trap_1)
    room.G1b.addObject(trap_2)

    # create treasures
    treasure = room.GloomhavenObject("Treasure_07", room.OBJ_TREASURE,[(4,10)])
    room.I1b.addObject(treasure)

    # create coins
    coin1 = room.GloomhavenObject("Coin", room.OBJ_COIN, [(2,0)])
    coin2 = room.GloomhavenObject("Coin", room.OBJ_COIN, [(3,1)])
    coin3 = room.GloomhavenObject("Coin", room.OBJ_COIN, [(4,0)])
    coin4 = room.GloomhavenObject("Coin", room.OBJ_COIN, [(2,10)])
    coin5 = room.GloomhavenObject("Coin", room.OBJ_COIN, [(3,9)])
    room.I1b.addObjects([coin1, coin2, coin3, coin4, coin5])
    print(table_1)

    # initialize map coordinates for all tiles
    # note: parameters are
    #    name of first room
    #    row to start at
    #    col to start at
    #    dictionary of room orientations/rotations with respect to first room (3 == up-side-down)
    m.mapCoordinates('L1a', 0, 0, {'G1b':3, 'I1b':0})

    # NPCs
    guards  = npc.NPCType("Bandit Guard", gv.monsterDataJson["Bandit Guard"])
    archers = npc.NPCType("Bandit Archer", gv.monsterDataJson["Bandit Archer"])
    #bones   = npc.NPCType("Living Bones", gv.monsterDataJson["Living Bones"])

    guard_1     = gv.SpawnUnit(guards, 0, 0, [npc.NONE, npc.NORMAL, npc.NORMAL])
    guard_2     = gv.SpawnUnit(guards, 1, 1, [npc.NONE, npc.NORMAL, npc.ELITE])
    guard_3     = gv.SpawnUnit(guards, 2, 0, [npc.NORMAL, npc.NORMAL, npc.NORMAL])
    guard_4     = gv.SpawnUnit(guards, 5, 1, [npc.ELITE, npc.NONE, npc.NONE])
    guard_5     = gv.SpawnUnit(guards, 4, 0, [npc.NORMAL, npc.NORMAL, npc.NORMAL])
    guard_6     = gv.SpawnUnit(guards, 5, 1, [npc.NONE, npc.NORMAL, npc.ELITE])
    guard_7     = gv.SpawnUnit(guards, 6, 0, [npc.NONE, npc.NORMAL, npc.NORMAL])

    room.L1a.addSpawns([guard_1, guard_2, guard_3, guard_4, guard_5, guard_6, guard_7])

    parents, cost = a_star_search(m, gv.Location(2, 8), gv.Location(10, -4))
    print("Can reach desired target in %d steps" % (len(parents)-1))
    print("Damage taken on path: %d" % (cost - (len(parents)-1)))
    print("Path is:\n", parents, "\n\n")

    m.setStartingRoom('L1a')
    m.spawnStartingRoom()

if __name__ == "__main__":
    scenario_1(4) # change arg to list of player objects