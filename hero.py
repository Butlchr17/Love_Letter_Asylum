class Hero:
    def __init__(self, name, psyche):
        self.name = name
        self.psyche = psyche # "Delusion", "Hysteria", etc...
        self.hp = 20
        self.max_hp = 20
        self.insanity = 0
        self.attack = 5
        self.defense = 3
        self.skills = ["Attack", "Calm"] # Expand this later
        self.affliction = None

    def take_damage(self, amount):
        self.hp -= max(0, amount - self.defense)
        if self.hp <= 0:
            return True # DEAD
        return False
    
    def add_insanity(self, amount):
        self.insanity = min(100, self.insanity + amount)
        if self.insanity >= 100 and not self.affliction:
            self.affliction = "Paranoia" # Randomize this later
    