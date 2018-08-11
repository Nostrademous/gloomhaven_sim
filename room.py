"""
"""

import global_vars as gv
from npc import NPC, NONE, ELITE
from character import Character

# DOOR TYPES
DOOR_TYPE_NONE              = 0
DOOR_TYPE_CLOSED            = 1
DOOR_TYPE_OPEN              = 2
DOOR_TYPE_PRESSURE_CLOSED   = 3
DOOR_TYPE_PRESSURE_OPEN     = 4

# OBJECT TYPES
OBJ_OBSTACLE    = 0
OBJ_TRAP        = 1
OBJ_HAZARD      = 2
OBJ_TREASURE    = 3
OBJ_COIN        = 4
OBJ_DIFFICULT   = 5

_obj_type_names = {
    "0": "Obstacle",
    "1": "Trap",
    "2": "Hazard",
    "3": "Treasure",
    "4": "Coin",
    "5": "Difficult"
}

class GloomhavenObject():
    def __init__(self, name, obj_type, tiles=[]):
        self.name       = name
        self.type       = obj_type
        self.tiles      = tiles
        self.destroyed  = False

    def __repr__(self):
        ret  = "[Object]: %s, [Type]: %s\n" % (self.name, _obj_type_names[str(self.type)])
        ret += "[Tile(s)]: %s\n" % (self.tiles)
        return ret

    def getTiles(self):
        return self.tiles

    def getType(self):
        return self.type

    def destroy(self):
        self.destroyed = True


class GloomhavenTile():
    def __init__(self, uuID, sides=6):
        self.unique_id  = uuID
        self.row_id, self.col_id = self.unique_id.rsplit(':')[1].split(',')
        self.row_id = int(self.row_id)
        self.col_id = int(self.col_id)
        self.num_sides  = sides
        self.neighbors  = list([None for i in range(sides)])
        #print("%s %d %s" % (self.unique_id, self.num_sides, self.neighbors))

        self.doorType = DOOR_TYPE_NONE

        # tile extra layers
        self.obstacle  = None
        self.trap      = None
        self.hazard    = None
        self.treasure  = None
        self.coins     = 0
        self.difficult = None

        # for path-finding and field of vision
        self.map_loc   = None

        # for recording presence of a unit
        self.unit      = None

    def __repr__(self):
        ret = "{%d,%d}" % (self.row_id, self.col_id)
        return ret

    def setRoomCoordinates(self, row, col):
        self.row_id = row
        self.col_id = col

    def setMapLocation(self, loc, roomRots):
        print("[%s] {%d,%d} updating map location to {%d,%d}" % (self.unique_id, self.row_id, self.col_id, loc.row, loc.col))
        self.map_loc = loc

    def getMapLocation(self):
        return self.map_loc

    def isPassable(self, hasJump=False, hasFlying=False, isPlayer=True):
        if (self.hasEnemy(isPlayer) or self.getObstacle()) and (not hasJump or not hasFlying):
            return False
        return True

    def costToEnter(self, scenDiff=1, hasJump=False, hasFlying=False):
        if hasJump or hasFlying:
            return 1
        else:
            if self.getTrap():
                return gv.calculateTrapDamage(scenDiff) + 1
            elif self.getHazard():
                return gv.calculateHazardDamage(scenDiff) + 1
            elif self.getDifficult():
                return 2
        return 1

    def setDoorType(self, doorType):
        self.doorType = doorType

    def isDoor(self):
        return self.doorType != DOOR_TYPE_NONE

    def isDoorOpen(self):
        return self.doorType in [DOOR_TYPE_OPEN, DOOR_TYPE_PRESSURE_OPEN]

    def hasEnemy(self, requestorIsPlayer=True):
        if not self.unit:
            return False
        if requestorIsPlayer and isinstance(self.unit, Character):
            return False
        return True

    def addObstacle(self, obstacle):
        self.obstacle = obstacle

    def addTrap(self, trap):
        self.trap = trap

    def addHazard(self, hazard):
        self.hazard = hazard

    def addTreasure(self, treasure):
        self.treasure = treasure

    def addCoin(self, amount=1):
        self.coins += amount

    def addDifficult(self, diff):
        self.difficult = diff

    def addUnit(self, unitType, unitList):
        assert gv.numPlayersInScenario >= 2 and gv.numPlayersInScenario <= 4

        if unitList[gv.numPlayersInScenario - 2] > NONE:
            elite = unitList[gv.numPlayersInScenario - 2] == ELITE
            self.unit = unitType.createEnemy(self.getMapLocation(), elite)
            assert self.unit
            print("Adding Unit %s\n" % (str(self.unit)))
            return self.unit
        return None

    def getCoins(self):
        return self.coins

    def getObstacle(self):
        return self.obstacle

    def getTrap(self):
        return self.trap

    def getHazard(self):
        return self.hazard

    def getDifficult(self):
        return self.difficult

    def getUnit(self):
        return self.unit

    def getTreasure(self):
        return self.hazard

    def findNeighborEdgeId(self, tile, orient):
        row_diff = tile.row_id - self.row_id
        col_diff = tile.col_id - self.col_id
        if orient == ORIENT_POINTY:
            if col_diff < 0 and row_diff == 0:
                return 3
            elif col_diff < 0 and row_diff < 0:
                return 4
            elif col_diff < 0 and row_diff > 0:
                return 2
            elif col_diff > 0 and row_diff == 0:
                return 0
            elif col_diff > 0 and row_diff > 0:
                return 1
            elif col_diff > 0 and row_diff < 0:
                return 5
            else:
                raise Exception("POINTY :: findNeighborEdgeId", "{%d,%d}" % (row_diff, col_diff))
        elif orient == ORIENT_FLAT:
            if row_diff < 0 and col_diff == 0:
                return 5
            elif row_diff < 0 and col_diff < 0:
                return 4
            elif row_diff < 0 and col_diff > 0:
                return 0
            elif row_diff > 0 and col_diff == 0:
                return 2
            elif row_diff > 0 and col_diff > 0:
                return 1
            elif row_diff > 0 and col_diff < 0:
                return 3
            else:
                raise Exception("FLAT :: findNeighborEdgeId", "{%d,%d}" % (row_diff, col_diff))

    def addNeighbor(self, sideID, tile, bidir=True):
        self.neighbors[sideID] = tile
        #print("Added Edge Between {%d,%d} and {%d,%d}" % (self.row_id, self.col_id, tile.row_id, tile.col_id))
        if bidir:
            tile.neighbors[(int(self.num_sides/2) + sideID) % self.num_sides] = self

    def getNeighbor(self, sideID):
        return self.neighbors[sideID]

    def getMapNeighbors(self):
        ret = list()
        for i in range(6):
            tile = self.getNeighbor(i)
            if tile:
                ret.append(tile.getMapLocation())
        return ret

    def printTile(self):
        ret = str(self)
        ret += " :: ["
        for indx,cell in enumerate(self.neighbors):
            ret += " %5s" % (cell)
        ret += "]\n"
        print(ret)

    def __lt__(self, other):
        return self.getMapLocation() < other.getMapLocation()


ORIENT_FLAT   = 1 # in hexagon flat edges are North & South
FLAT_EDGES    = [(-1, 1), (1,1), (2,0), (1,-1), (-1,-1), (-2,0)]
ORIENT_POINTY = 2 # in hexagon flat edges are West & East
POINTY_EDGES  = [(0,2), (1,1), (1,-1), (0,-2), (-1,-1), (-1, 1)]
class GloomhavenRoom():
    def __init__(self, name, orientation=ORIENT_FLAT, max_rows=1, max_cols=1, tilePattern=[]):
        self.name           = name
        self.orient         = orientation
        self.max_r          = max_rows
        self.max_c          = max_cols
        self.tilePattern    = tilePattern
        self.tiles          = list()

        if len(self.tilePattern) > 0:
            self.fillPattern()

        # members specific to rooms in a map
        self.open           = False
        self.npc_spawn_locs = list()

        self.hero_start_locs= list()

    def __repr__(self):
        ret  = "Room: %s\n" % (self.name)
        return ret

    def getName(self):
        return self.name

    def getOrientation(self):
        return self.orient

    def setOpen(self):
        self.open = True

    def getTile(self, row, col):
        #print("[getTile] {%d,%d}" % (row, col))
        for tile in self.tiles:
            #print("[test] {%d,%d}" % (tile.row_id, tile.col_id))
            if tile.row_id == row and tile.col_id == col:
                return tile
        return None

    def addPlayerStartLocs(self, locs):
        for loc in locs:
            self.hero_start_locs.append(loc)

    def addSpawns(self, npcList):
        for npc in npcList:
            assert isinstance(npc, gv.SpawnUnit)
            self.npc_spawn_locs.append(npc)

    def spawnNPCs(self):
        assert self.open # only spawn when room is "seen"
        new_npcs = list()

        for npc in self.npc_spawn_locs:
            assert isinstance(npc, gv.SpawnUnit)

            spawnTile = self.getTile(npc.row, npc.col)
            if spawnTile:
                new_npc = spawnTile.addUnit(npc.unitType, npc.numPlayerList)
                if new_npc:
                    new_npcs.append(new_npc)
            else:
                raise Exception("GloomhavenRoom", "addNPCs - failed to find {%d,%d}" % (npc.row, npc.col))
        return new_npcs

    def addObjects(self, objects):
        for object in objects:
            self.addObject(object)

    def addObject(self, object):
        for loc in object.getTiles():
            tile = self.getTile(loc[0], loc[1])
            if tile:
                if object.getType() == OBJ_OBSTACLE:
                    tile.addObstacle(object)
                elif object.getType() == OBJ_TREASURE:
                    tile.addTreasure(object)
                elif object.getType() == OBJ_TRAP:
                    tile.addTrap(object)
                elif object.getType() == OBJ_HAZARD:
                    tile.addHazard(object)
                elif object.getType() == OBJ_DIFFICULT:
                    tile.addDifficult(object)
                elif object.getType() == OBJ_COIN:
                    for loc in object.getTiles():
                        tile = self.getTile(loc[0], loc[1])
                        if tile:
                            tile.addCoin(1)
            else:
                raise Exception("[GloomhavenRoom]", "No Tile at Coord {%d,%d}" % (loc[0], loc[1]))

    def printRoom(self):
        print("ROOM: %s [%d x %d]" % (self.name.upper(), self.max_r, self.max_c))
        for tile in self.tiles:
            tile.printTile()

    def getTileByMapCoordinates(self, loc):
        for tile in self.tiles:
            tile_loc = tile.getMapLocation()
            if tile_loc == loc:
                return tile
        return None

    def getFillPatternValue(self, r, c):
        if r < 0 or c < 0: return 0
        elif r >= self.max_r or c >= self.max_c: return 0
        #print('FillPatternIndx: %d' % (r*(self.max_c)+c))
        return self.tilePattern[r*(self.max_c) + c]

    """
        fill pattern assumes layout:
        row      0   1   2   3   4   5   <-- column
         0      0,0     0,2     0,4
         1          1,1     1,3     1,5
         2      2,0     2,2     2,4
         3          3,1     3,3     3,5
         4      4,0     4,2     4,4
    """
    def fillPattern(self):
        assert len(self.tilePattern) == (self.max_r * self.max_c)

        indx = 0
        for r in range(self.max_r):
            for c in range(self.max_c):
                indx = r*self.max_c + c
                if self.tilePattern[indx] > 0:
                    #print("Creating Tile {%d,%d}" % (r,c))
                    new_tile = GloomhavenTile(self.name+':%d,%d' % (r,c))
                    self.tiles.append(new_tile)
                    if self.orient == ORIENT_FLAT:
                        north_east  = self.getFillPatternValue(r-1, c+1)
                        if north_east:
                            #print('NE Exists {%d,%d}' % (r-1, c+1))
                            new_tile.addNeighbor(0, self.getTile(r-1, c+1))
                        north_west  = self.getFillPatternValue(r-1, c-1)
                        if north_west:
                            new_tile.addNeighbor(4, self.getTile(r-1, c-1))
                        north       = self.getFillPatternValue(r-2, c)
                        if north:
                            new_tile.addNeighbor(5, self.getTile(r-2, c))
                    elif self.orient == ORIENT_POINTY:
                        west        = self.getFillPatternValue(r, c-2)
                        if west:
                            new_tile.addNeighbor(3, self.getTile(r, c-2))
                        north_west  = self.getFillPatternValue(r-1, c-1)
                        if north_west:
                            new_tile.addNeighbor(4, self.getTile(r-1, c-1))
                        north_east  = self.getFillPatternValue(r-1, c+1)
                        if north_east:
                            #print('NE Exists {%d,%d}' % (r-1, c+1))
                            new_tile.addNeighbor(5, self.getTile(r-1, c+1))
                    else:
                        raise Exception('[Unknown Room Orientation]', self.orient)

# Glooomhaven Room Layouts
G1b = GloomhavenRoom('G1b', orientation=ORIENT_POINTY, max_rows=3, max_cols=15,
    tilePattern=[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

I1b = GloomhavenRoom('I1b', orientation=ORIENT_POINTY, max_rows=5, max_cols=11,
    tilePattern=[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

L1a = GloomhavenRoom('L1a', orientation=ORIENT_POINTY, max_rows=7, max_cols=9,
    tilePattern=[1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1,
                 0, 1, 0, 1, 0, 1, 0, 1, 0,
                 1, 0, 1, 0, 1, 0, 1, 0, 1,])

if __name__ == "__main__":
    #"""
    # Test 1
    t11 = GloomhavenTile("M1b:1,1")
    t12 = GloomhavenTile("M1b:2,2")
    t11.addNeighbor(5, t12)
    t11.printTile()
    t12.printTile()
    print(t11.findNeighborEdgeId(t12, ORIENT_POINTY))
    #"""

    """
    # Test 2
    G1b.printRoom()
    I1b.printRoom()
    L1a.printRoom()
    """
