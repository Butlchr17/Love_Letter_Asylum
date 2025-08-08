class Hero:
    
    # Hero base stats. Currently these are fixed. Needs updating with level-based scaling and unique classes
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
        damage = max(0, amount - self.defense)
        self.hp -= damage
        self.add_insanity(damage * 2)
        return damage > 0
    

    # Insanity and Afflictions, needs updating with periodic checks and worsening effects at 100 insanity
    def add_insanity(self, amount):
        self.insanity = max(0, min (100, self.insanity + amount))
        if self.insanity >= 100 and not self.affliction:
            afflictions = ["Paranoia", "Mania", "Catatonia"]
            self.affliction = random.choice(afflictions)
            if self.affliction == "Mania":
                self.attack += 2
                self.defense -= 1
            elif self.affliction == "Catatonia":
                self.attack -= 2

    def __dict__(self):
        return {
            "name": self.name,
            "psyche": self.psyche,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "insanity": self.insanity,
            "attack": self.attack,
            "defense": self.defense,
            "affliction": self.affliction
        }