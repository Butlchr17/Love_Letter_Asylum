"""
Basic prototype of exploration levels. These need updating with better randomization, enemy thematics, and map designs.
"""

import random

class Asylum:
    def __init__(self, level):
        self.level = level
        self.theme = self.get_theme()
        self.map = self.get_predefined_map()
        self.player_pos = (0, 0)  # Start at beginning of area map
        self.goals_completed = False
    
    # Define themes of each of the Asylum's Wards (levels)
    def get_theme(self):
        themes = {
            1: "General Admission",
            2: "Isolation Area",
            3: "Therapy Department",
            4: "Madman's Laboratory",
            5: "Director's Quarters"
        }
        return themes.get(self.level, "Unknown Ward")
    
    def get_predefined_map(self):
        
        # General Admission (Introduction and level 1)
        if self.level == 1:
            return [
                ["empty", "therapy", "shock_trap", "empty"],
                ["hallucination", "empty", "letter", "empty", "therapy"],
                ["empty", "shock_trap", "empty", "empty", "empty"],
                ["therapy", "empty", "empty", "hallucination", "key"],
                ["empty", "empty", "therapy", "empty", "boss_room"]
            ]

        # Isolation Area (More traps than normal)
        elif self.level == 2:
            return [
                ["shock_trap", "empty", "hallucination", "empty", "shock_trap"],
                ["empty", "therapy", "empty", "shock_trap", "empty"],
                ["hallucination", "empty", "letter", "empty", "hallucination"],
                ["shock_trap", "empty", "therapy", "empty", "key"],
                ["empty", "shock_trap", "empty", "empty", "boss_room"]
            ]

        # Therapy Department (More combats than normal)
        elif self.level == 3:
            return [
                ["therapy", "empty", "therapy", "empty", "letter"],
                ["empty", "therapy", "empty", "therapy", "empty"],
                ["therapy", "empty", "hallucination", "empty", "therapy"],
                ["empty", "therapy", "empty", "key", "empty"],
                ["therapy", "empty", "therapy", "empty", "boss_room"]
            ]

        # Madman's Laboratory (Mixed amounts of traps and hallucinations are more common)
        elif self.level == 4:
            return [
                    ["shock_trap", "hallucination", "empty", "shock_trap", "hallucination"],
                    ["empty", "shock_trap", "letter", "hallucination", "empty"],
                    ["hallucination", "empty", "shock_trap", "empty", "shock_trap"],
                    ["shock_trap", "hallucination", "empty", "key", "hallucination"],
                    ["empty", "shock_trap", "hallucination", "empty", "boss_room"]
                ]
        
        # Director's Quarters (Elite Enemies and end of main storyline)
        elif self.level == 5:
            return [
                ["therapy", "shock_trap", "hallucination", "therapy", "letter"],
                ["empty", "therapy", "empty", "shock_trap", "hallucination"],
                ["hallucination", "empty", "therapy", "empty", "therapy"],
                ["shock_trap", "hallucination", "empty", "key", "empty"],
                ["therapy", "empty", "hallucination", "therapy", "boss_room"]
            ]

        # Fallback level (for bug catching)
        return [["empty"] * 5 for _ in range(5)]