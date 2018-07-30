'''
'''

_item_slots = list([
    "HEAD", "BODY", "HAND", "HANDS", "FEET", "POTION"
])

class Item():
    def __init__(self, id, name, slot, maxCnt, cost=0, maxUses=1):
        try:
            assert slot in _item_slots
            self.id         = id
            self.name       = name
            self.slot       = slot
            self.maxCount   = maxCnt
            self.used       = False
            self.useCount   = 0
            self.maxUses    = maxUses
            self.desc       = ""
            self.cost       = cost
        except AssertionError as err:
            print("[Item __init__ :: AssertionError] %s" % (err))
            print("SLOT: %s" % (slot))
            raise

    def setDesc(self, text):
        self.desc = text

    def getDesc(self):
        return self.desc

    def use(self):
        self.useCount += 1
        if self.useCount >= self.maxUses:
            self.used = True

    def reset(self):
        self.used = False
        self.useCount = 0

    def sellCost(self):
        return int(self.cost/2.)

    def __repr__(self):
        ret  = "[Item %d] %s\n" % (self.id, self.name)
        ret += "Slot: %s\n" % (self.slot)
        ret += "Max Available: %d\n" % (self.maxCount)
        ret += "Cost: %d gold\n" % (self.cost)
        ret += "%d uses before tapped\n" % self.maxUses
        return ret

if __name__ == "__main__":
    import global_vars as gv
    gv.init()
    
    for item in gv.itemDataJson:
        itemData = gv.itemDataJson[item]
        item_obj = Item(int(item), itemData['Name'], itemData['Slot'].upper(), itemData['MaxCount'],
                        cost=itemData['Cost'], maxUses=itemData['Buff']['Count'])
        print(item_obj)
