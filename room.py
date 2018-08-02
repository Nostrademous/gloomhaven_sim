"""
"""

DOOR_TYPE_NONE              = 0
DOOR_TYPE_CLOSED            = 1
DOOR_TYPE_OPEN              = 2
DOOR_TYPE_PRESSURE_CLOSED   = 3
DOOR_TYPE_PRESSURE_OPEN     = 4

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
        self.hasObstacle    = None
        self.hasTrap        = None
        self.hasHazard      = None
        self.hasTreasure    = None
        self.hasCoin        = None

    def __repr__(self):
        ret = "{%d,%d}" % (self.row_id, self.col_id)
        return ret

    def setRoomCoordinates(self, row, col):
        self.row_id = row
        self.col_id = col

    def setDoorType(self, doorType):
        self.doorType = doorType

    def isDoor(self):
        return self.doorType != DOOR_TYPE_NONE

    def isDoorOpen(self):
        return self.doorType in [DOOR_TYPE_OPEN, DOOR_TYPE_PRESSURE_OPEN]

    def addObstacle(self, obstacle):
        self.hasObstacle = obstacle

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

    def printTile(self):
        ret = str(self)
        ret += " :: ["
        for indx,cell in enumerate(self.neighbors):
            ret += " %5s" % (cell)
        ret += "]\n"
        print(ret)

class Object():
    def __init__(self, name, tiles=[]):
        self.name       = name
        self.tiles      = tiles
        self.destroyed  = False

    def __repr__(self):
        ret  = "[Object]: %s\n" % (self.name)
        ret += "[Tile(s)]: %s\n" % (self.tiles)
        return ret

    def getTiles(self):
        return self.tiles

    def destroy(self):
        self.destroyed = True

ORIENT_FLAT   = 1 # in hexagon flat edges are North & South
ORIENT_POINTY = 2 # in hexagon flat edges are West & East
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

    def __repr__(self):
        ret  = "Room: %s\n" % (self.name)
        return ret

    def getName(self):
        return self.name

    def getOrientation(self):
        return self.orient

    def getTile(self, row, col):
        #print("[getTile] {%d,%d}" % (row, col))
        for tile in self.tiles:
            #print("[test] {%d,%d}" % (tile.row_id, tile.col_id))
            if tile.row_id == row and tile.col_id == col:
                return tile
        return None

    def addObstacle(self, obstacle):
        for loc in obstacle.getTiles():
            tile = self.getTile(loc[0], loc[1])
            if tile:
                tile.addObstacle(obstacle)
            else:
                raise Exception("[GloomhavenRoom]", "No Tile at Coord {%d,%d}" % (loc[0], loc[1]))

    def printRoom(self):
        print("ROOM: %s [%d x %d]" % (self.name.upper(), self.max_r, self.max_c))
        for tile in self.tiles:
            tile.printTile()

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
