'''
'''

from unit import Unit
import global_vars as gv
from utils import pickRandom

def createEnemy(name, numNormal=0, numElite=0, numBoss=0, isSpawn=False):
    bossList = list()
    eliteList = list()
    normalList = list()

    mob = gv.monsterDataJson[name]

    slot_id = 1
    for cnt in range(numBoss):
        bossList.append(NPC(name, mob["DeckType"], slot_id, boss=True))
        slot_id += 1
    for cnt in range(numElite):
        eliteList.append()
        slot_id += 1
    for cnt in range(numNormal):
        eliteList.append(NPC(name, mob["DeckType"], slot_id, spawn=isSpawn))
        slot_id += 1
    return normalList, eliteList, bossList


class NPCType():
    def __init__(self, name, monsterData, difficulty=1):
        self.name           = name
        self.data           = monsterData
        self.stat_data      = monsterData["Stats"]
        self.deck_name      = monsterData["DeckType"]
        self.difficulty     = difficulty
        self.available_ids  = [i for i in range(1, monsterData["Slots"]+1)]
        try:
            self.full_deck      = gv.monsterDeckDataJson[self.deck_name]
        except KeyError as err:
            print("Ability Deck for %s is not yet implemented!" % (self.name))
            self.full_deck      = dict()
        self.curr_deck      = dict(self.full_deck)
        self.curr_units     = list()

    def createEnemy(self, elite=False, isSpawn=False):
        if len(self.available_ids) > 0:
            selected_id = self.available_ids[0]
            self.available_ids.remove(selected_id)
            self.curr_units.append(NPC(self.name, self.stat_data[str(self.difficulty)], selected_id,
                                       elite=elite, boss=self.deck_name == "Boss", spawn=isSpawn))
        else:
            print("Cannot Create Enemy: '%s'%" % (self.name))

    def reshuffleDeck(self):
        self.curr_deck = dict(self.full_deck)

    def printUnits(self):
        for unit in self.curr_units:
            print(unit)


class NPC(Unit):
    def __init__(self, name, statData, slot_id=1, elite=False, spawn=False, boss=False):
        super().__init__(name)
        self.slot_id    = slot_id
        self.elite      = elite
        self.spawn      = spawn
        self.buffs      = list()
        self.move       = 0
        self.attack     = 0
        self.range      = 0
        self.immunities = list()
        self.causes     = list()
        self.boss       = boss

        if elite:
            self.stats   = statData["Elite"]
        else:
            self.stats  = statData["Normal"]

        # set values
        self.setHealth(self.stats["Health"])
        self.setBuffs(self.stats["Buffs"])
        self.setImmunities(self.stats["Immunities"])
        self.setCauses(self.stats["Effects"])
        self.setMAR(self.stats["Movement"], self.stats["Attack"], self.stats["Range"])

    def setHealth(self, value, numPlayers=1):
        if self.isBoss():
            super().setHealth(value * numPlayers)
        else:
            super().setHealth(value)

    def takeDamage(self, amount, effList=[]):
        self.curr_hp = max(self.curr_hp - amount, 0)
        if self.curr_hp > 0:
            self.effects.extend(effList)

    def setMAR(self, move, attack, range):
        self.move   = int(move)
        self.attack = int(attack)
        self.range  = int(range)

    def setBuffs(self, buffList):
        self.buffs.extend(buffList)

    def setImmunities(self, immuneList):
        self.immunities.extend(immuneList)

    def setCauses(self, causeList):
        self.causes.extend(causeList)

    def canAttack(self):
        return self.attack > 0 and not hasEffect(self.effects, "Disarm") and not hasEffect(self.effects, "Stun")

    def canMove(self):
        return self.move > 0 and not hasEffect(self.effects, "Immobilize") and not hasEffect(self.effects, "Stun")

    def isMelee(self):
        return self.range == 0

    def isRanged(self):
        return self.range > 0

    def isDead(self):
        return self.curr_hp <= 0

    def isElite(self):
        return self.elite

    def isSpawn(self):
        return self.spawn

    def isBoss(self):
        return self.boss

    def isFlying(self):
        return "Flying" in self.buffs

    def shieldValue(self):
        for buff in self.buffs:
            if "Shield" == buff[:6]:
                return int(buff[7:])
        return 0

    def __repr__(self):
        ret  = super().__repr__()
        sType = "Normal"
        if self.isElite():
            sType = "Elite"
        ret += "Type: %s\n" % (sType)
        ret += "Health: %d, Move: %d, Attack: %d, Range: %d\n" % (self.curr_hp, self.move, self.attack, self.range)
        if len(self.buffs) > 0:
            ret += "Buffs: %s\n" % (self.buffs)
        if len(self.immunities) > 0:
            ret += "Immunities: %s\n" % (self.immunities)
        if len(self.causes) > 0:
            ret += "Causes Effects: %s\n" % (self.causes)
        return ret


if __name__ == "__main__":
    for monName in gv.monsterDataJson.keys():
        mon_type = NPCType(monName, gv.monsterDataJson[monName])
        mon_type.createEnemy(elite=pickRandom([True, False]))
        mon_type.printUnits()
