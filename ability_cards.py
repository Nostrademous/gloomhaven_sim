'''
'''

class AbilityCard():
    def __init__(self, id, name, level):
        self.id     = id
        self.name   = name
        self.level  = level
    
    def __repr__(self):
        return "[%d] %s\nLevel: %d\n" % (self.id, self.name, self.level)

if __name__ == "__main__":
    card = AbilityCard(37, "Reinvigorating Elixir", 1)
    print(card)