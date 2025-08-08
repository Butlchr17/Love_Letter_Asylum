"""
This is an EXTREMELY simplistic enemy character class and NEEDS updating when specific enemies are designed.
"""

import random

class Enemy:
    def __init__(self, name, level, is_boss = False):
        self.name = name
        self.level = level
        self.hp = 10 * level
        self.attack = 3 * level
        self.defense = level
        if is_boss:
            self.hp *=3
            self.attack = int(self.attack * 1.5)
            self.defense += 2

    def act(self, target):
        damage = target.take_damage(self.attack)
        if random.random() < 0.3:
            target.add_insanity(10)
        return damage
