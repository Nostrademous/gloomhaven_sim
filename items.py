'''
'''

SLOT_HEAD   = "1"
SLOT_BODY   = "2"
SLOT_HAND   = "3"
SLOT_HANDS  = "4"
SLOT_FEET   = "5"
SLOT_POTION = "6"

_item_slots = {
    SLOT_HEAD: "HEAD",
    SLOT_BODY: "BODY",
    SLOT_HAND: "HAND",
    SLOT_HANDS: "HANDS",
    SLOT_FEET: "FEET",
    SLOT_POTION: "POTION"
}

def slotStr(slotID):
    if str(slotID) in _item_slots.keys():
        return _item_slots[str(slotID)]
    else:
        raise Exception('Unknown slotID Name: %s' % slotID)

class Item():
    def __init__(self, id, name, slot, maxUses=1):
        try:
            assert slot in _item_slots.keys()
            self.id         = id
            self.name       = name
            self.slot       = slot
            self.used       = False
            self.useCount   = 0
            self.maxUses    = maxUses
        except AssertionError as err:
            print("[Item __init__ :: AssertionError] %s" % (err))
            raise

    def use(self):
        self.useCount += 1
        if self.useCount >= self.maxUses:
            self.used = True

    def reset(self):
        self.used = False
        self.useCount = 0

    def __repr__(self):
        ret  = "[Item %d] %s\n" % (self.id, self.name)
        ret += "Slot: %s\n" % (slotStr(self.slot))
        ret += "%d uses before tapped\n" % self.maxUses
        return ret

if __name__ == "__main__":
    item = Item(0, 'Potion', SLOT_POTION)
    print(item)
