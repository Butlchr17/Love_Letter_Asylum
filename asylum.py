import random

class Asylum:
    def __init__(self, level):
        self.level = level
        self.map = self.generate_map(5, 5) # 2D list of rooms
        self.player_pos = (0, 0) # Start at entrance ward

    def generate_map(self, width, height):
        map_grid = [["empty" for _ in range(width)] for _ in range(height)]

        # Add some random events
        for _ in range(5):
            x, y = random.randint(0, width-1), random.randint(0, height-1) 
            map_grid[x][y] = random.choice(["shock_trap", "hallucination", "therapy", "letter"])
        return map_grid

    def move(self, direction):
        # Update player_pos (handle bounds)
        # trigger room event
        room = self.map[self.player_pos[1]][self.player_pos[0]]
        if room == "therapy":
            return "start_therapy"
        elif room == "letter":
            return "found_letter"
        elif room == "shock_trap":
            return "trigger_trap" # Adds insanity to party
        return None