"""
"""

class GloomhavenTile():
    def __init__(self, uuID, sides=6):
        self.unique_id  = uuID
        self.row_id, self.col_id = self.unique_id.rsplit('-')[1].split(',')
        self.row_id = int(self.row_id)
        self.col_id = int(self.col_id)
        self.num_sides  = sides
        self.neighbors  = list([None for i in range(sides)])
        #print("%s %d %s" % (self.unique_id, self.num_sides, self.neighbors))

    def __repr__(self):
        ret  = "[%s] {row: %d, col: %d}" % (self.unique_id, self.row_id, self.col_id)
        return ret

    def addNeighbor(self, sideID, tile, bidir=True):
        self.neighbors[sideID] = tile
        if bidir:
            tile.neighbors[(int(self.num_sides/2) + sideID) % self.num_sides] = self

    def printTile(self):
        ret = str(self)
        ret += " :: ["
        for indx,cell in enumerate(self.neighbors):
            ret += " %s" % (cell)
        ret += "]\n"
        print(ret)

ORIENT_FLAT   = 1 # in hexagon flat edges are North & South
ORIENT_POINTY = 2 # in hexagon flat edges are West & East
class GloomhavenRoom():

    def __init__(self, name, orientation=ORIENT_FLAT, max_rows=1, max_cols=1):
        self.name   = name
        self.orient = orientation
        self.max_r  = max_rows
        self.max_c  = max_cols
        self.tiles  = list()

    def __repr__(self):
        ret  = "Room: %s\n" % (self.name)
        return ret

    def getTile(self, row, col):
        for tile in self.tiles:
            if tile.row_id == row and tile.col_id == col:
                return tile
        return None
    
    def printRoom(self):
        print(self)
        for tile in self.tiles:
            tile.printTile()

    def getFillPatternValue(self, r, c):
        if r < 0 or c < 0: return 0
        elif r > self.max_r or c > self.max_c: return 0
        #print('FillPatternIndx: %d' % (r*(self.max_c)+c))
        return self.fillPattern[r*(self.max_c) + c]

    """
        fill pattern assumes layout:
        row      0   1   2   3   4   5   <-- column
         0      0,0     0,2     0,4
         1          1,1     1,3     1,5
         2      2,0     2,2     2,4
         3          3,1     3,3     3,5
         4      4,0     4,2     4,4
    """
    def fillPattern(self, fillList):
        assert len(fillList) == (self.max_r * self.max_c)
        self.fillPattern = fillList

        indx = 0
        for r in range(self.max_r):
            for c in range(self.max_c):
                indx = r*self.max_c + c
                if fillList[indx] > 0:
                    new_tile = GloomhavenTile(self.name+'-%d,%d' % (r,c))
                    self.tiles.append(new_tile)
                    if self.orient == ORIENT_FLAT:
                        if r > 0:
                            north_east  = self.getFillPatternValue(r-1, c+1)
                            if north_east:
                                new_tile.addNeighbor(0, self.getTile(r-1, c+1))
                            north_west  = self.getFillPatternValue(r-1, c-1)
                            if north_west:
                                new_tile.addNeighbor(4, self.getTile(r-1, c-1))
                            north       = self.getFillPatternValue(r-2, c)
                            if north:
                                new_tile.addNeighbor(5, self.getTile(r-2, c))
                    elif self.orient == ORIENT_POINTY:
                        if c > 0:
                            west        = self.getFillPatternValue(r, c-2)
                            if west:
                                new_tile.addNeighbor(3, self.getTile(r, c-2))
                            north_west  = self.getFillPatternValue(r-1, c-1)
                            if north_west:
                                new_tile.addNeighbor(4, self.getTile(r-1, c-1))
                            north_east  = self.getFillPatternValue(r-1, c+1)
                            if north_east:
                                new_tile.addNeighbor(5, self.getTile(r-1, c+1))
                    else:
                        raise Exception('[Unknown Room Orientation]', self.orient)

if __name__ == "__main__":
    t11 = GloomhavenTile("M1b-1,1")
    t12 = GloomhavenTile("M1b-1,2")
    t11.addNeighbor(5, t12)
    t11.printTile()
    t12.printTile()

    room = GloomhavenRoom('M1b', max_rows=5, max_cols=6)
    room.fillPattern([1, 0, 1, 0, 1, 0,
                      0, 1, 0, 1, 0, 1,
                      1, 0, 1, 0, 1, 0,
                      0, 1, 0, 1, 0, 1,
                      1, 0, 1, 0, 1, 0])
    room.printRoom()


    room = GloomhavenRoom('M1b', max_rows=5, max_cols=6, orientation=ORIENT_POINTY)
    room.fillPattern([1, 0, 1, 0, 1, 0,
                      0, 1, 0, 1, 0, 1,
                      1, 0, 1, 0, 1, 0,
                      0, 1, 0, 1, 0, 1,
                      1, 0, 1, 0, 1, 0])
    room.printRoom()
