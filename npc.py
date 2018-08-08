'''
'''

from unit import Unit
import global_vars as gv
from utils import pickRandom

class NPCAbility():
    def __init__(self, num, jsonData):
        #print(jsonData)
        self.num            = num
        self.initiative     = jsonData['Initiative']
        self.actions        = jsonData['Actions']
        self.reshuffle      = False
        if 'Reshuffle' in jsonData:
            self.reshuffle  = True

    def __repr__(self):
        ret  = '[%d]\n' % self.num
        ret += 'Initiative: %d\n' % self.initiative
        if self.reshuffle:
            ret += 'RESHUFFLE AT TURN END\n'
        ret += str(self.actions)
        return ret

def parseMonsterDeck(deck):
    abilities = list()
    #print(deck)
    for num in deck:
        #print(num)
        abilities.append(NPCAbility(int(num), deck[num]))
    return abilities

class NPCType():
    def __init__(self, name, monsterData, difficulty=1):
        self.name           = name
        self.data           = monsterData
        self.stat_data      = monsterData["Stats"]
        self.deck_name      = monsterData["DeckType"]
        self.difficulty     = difficulty
        self.available_ids  = [i for i in range(1, monsterData["Slots"]+1)]
        try:
            self.full_deck      = list(parseMonsterDeck(gv.monsterDeckDataJson[self.deck_name]))
        except KeyError as err:
            print("Ability Deck for %s is not yet implemented!" % (self.name))
            self.full_deck      = list()
        self.curr_deck      = list(self.full_deck)
        self.curr_ability   = None
        self.curr_units     = list()

    def createEnemy(self, cellLoc=gv.Location(0,0), elite=False, isSpawn=False):
        if len(self.available_ids) > 0:
            selected_id = self.available_ids[0]
            self.available_ids.remove(selected_id)
            if isinstance(cellLoc, tuple):
                cellLoc = gv.Location(cellLoc[0], cellLoc[1])
            self.curr_units.append(NPC(self.name, self.stat_data[str(self.difficulty)], selected_id,
                                       cellLoc, elite=elite, boss=self.deck_name == "Boss", 
                                       spawn=isSpawn))
        else:
            print("Cannot Create Enemy: '%s'%" % (self.name))

    def drawRoundAbility(self):
        assert len(self.curr_deck) > 0
        self.curr_ability = pickRandom(self.curr_deck)
        self.curr_deck.remove(self.curr_ability)
        print(self.curr_ability)

    def endTurn(self):
        assert self.curr_ability != None
        if self.curr_ability.reshuffle:
            self.reshuffleDeck()
        self.curr_ability = None
        print("Remain Number of Ability Cards: %d\n\n" % (len(self.curr_deck)))

    def reshuffleDeck(self):
        self.curr_deck = list(self.full_deck)

    def updateUnits(self):
        dead_units = []
        for unit in self.curr_units:
            if unit.getHealth() == 0:
                dead_units.append(unit)

        # can't do this as part of the above iteration as
        # we would be modifying the list we are iterating over
        for unit in dead_units:
            self.destroyEnemy(unit)

    def destroyEnemy(self, npc):
        assert npc in self.curr_units
        self.available_ids.append(npc.slot_id)
        self.curr_units.remove(npc)

    def printUnits(self):
        for unit in self.curr_units:
            print(unit)



class NPC(Unit):
    def __init__(self, name, statData, slot_id, cellLoc, elite=False, spawn=False, boss=False):
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
        self.effects    = list()
        self.boss       = boss
        self.location   = cellLoc

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

    def getHealth(self):
        return self.curr_hp

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
        ret += "Slot ID: %d\n" % (self.slot_id)
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
        ret += "Map Location: {%d,%d}\n" % (self.location.row, self.location.col)
        return ret


if __name__ == "__main__":
    for monName in gv.monsterDataJson.keys():
        mon_type = NPCType(monName, gv.monsterDataJson[monName])
        mon_type.createEnemy(cellLoc=(1,1), elite=pickRandom([True, False]))
        mon_type.createEnemy(gv.Location(2,2), elite=pickRandom([True, False]))
        mon_type.createEnemy(elite=pickRandom([True, False]))
        mon_type.printUnits()

        for i in range(10):
            mon_type.drawRoundAbility()
            mon_type.endTurn()
