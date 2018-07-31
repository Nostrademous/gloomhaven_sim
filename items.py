'''
'''

_item_slots = list([
    "HEAD", "BODY", "ONE_HAND", "TWO_HANDS", "LEGS", "SMALL_ITEM"
])

class Item():
    def __init__(self, id, name, slot, maxCnt, cost=0, maxUses=1):
        try:
            assert slot.upper() in _item_slots
            self.id         = id
            self.name       = name
            self.slot       = slot
            self.maxCount   = maxCnt
            self.used       = False
            self.useCount   = 0
            self.maxUses    = maxUses
            self.desc       = ""
            self.cost       = cost
            self.amdEffect  = None
            self.buff       = None
            self.consumed   = False
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

    def setBuff(self, buff):
        self.buff = buff

    def setConsumable(self, value):
        self.consumed = value

    def setAMDEffect(self, effect):
        self.amdEffect = effect

    def affectsAMD(self):
        if self.amdEffect: return True
        return False

    def getBuffType(self):
        return self.buff['Type']

    def grantsSummon(self):
        if self.getBuffType().upper() == "SUMMON":
            return True
        return False

    def __repr__(self):
        ret  = "[Item %d] %s\n" % (self.id, self.name)
        ret += "Slot: %s\n" % (self.slot)
        ret += "Max Available: %d\n" % (self.maxCount)
        ret += "Cost: %d gold\n" % (self.cost)
        if self.buff:
            ret += "Provides following buff:\n"
            if self.buff["Type"] == "Debuff":
                ret += "    Debuff Enemy: %s\n" % (self.buff["Debuff"])
            else:
                if self.grantsSummon():
                    ret += "    Summon: %s {HP: %d, Move: %d, Att: %d, Rng: %d}\n" % (self.buff["Name"],
                            self.buff["Health"], self.buff["Move"], self.buff["Attack"], self.buff["Range"])
                else:
                    ret += "    Buff: %s\n" % (self.buff["Buff"])
            if "Trigger" in self.buff:
                ret += "    Trigger: %s\n" % (self.buff["Trigger"])
        if self.consumed:
            ret += "%d uses before consumed\n" % self.maxUses
        else:
            ret += "%d uses before tapped\n" % self.maxUses
        if self.affectsAMD():
            ret += "Affects Attack Modifier Deck\n"
            ret += "    Add %d %d cards\n" % (self.amdEffect['Count'], self.amdEffect['Value'])
        return ret

if __name__ == "__main__":
    import global_vars as gv
    gv.init()

    for item in gv.itemDataJson:
        itemData = gv.itemDataJson[item]
        item_obj = Item(int(item), itemData['Name'], itemData['Slot'].upper(), itemData['MaxCount'],
                        cost=itemData['Cost'], maxUses=itemData['Buff']['Count'])
        if "AMDEffect" in itemData:
            item_obj.setAMDEffect(itemData["AMDEffect"])
        if "Buff" in itemData:
            item_obj.setBuff(itemData["Buff"])
        if "Consumed" in itemData:
            item_obj.setConsumable(itemData["Consumed"])
        print(item_obj)
