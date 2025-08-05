import random

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "sanctuary" # States: sanctuary (safe hub outside asylum), ward (exploration), therapy(combat)
        self.party = [] # List of heros in current party
        self.inventory = {"sedatives": 10, "keys": 5}
        self.letters_collected = [] # List of love letters (story progression items)

    def update(self):
        pass # Handle logic based on state
    
    def draw(self):
        self.screen.fill((0,0,0)) # Black background for dark theme

        # Draw more UI elements:
    
    def recruit_inmate(self):
        pysches = ["Delusion", "Hysteria", "Obsession", "Phobia"]
        psyche = random.choice(psyches)
        hero = Hero(f"Inmate {len(self.party) + 1}", psyche)
        if len(self.party) < 4: # Party size limit of 4
            self.party.append(hero)