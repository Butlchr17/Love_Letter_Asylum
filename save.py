"""
Saves game states and all necessary stats/collectables/completion awards

This needs updating as game is further created in order to save additional stuff

Currently assumes all fields exist. Add defaults or try-except for missing keys to handle partial saves
"""

import json

def save_game(game, filename="save.json"):
    data = {
        "party": [h.__dict__ for h in game.party],
        "dead_heroes": [h.__dict__ for h in game.dead_heroes],
        "inventory": game.inventory,
        "letters_collected": game.letters_collected,
        "state": game.state,
        "asylum": {
            "level": game.asylum.level if game.asylum else 0,
            "map": game.asylum.map if game.asylum else None,
            "player_pos": game.asylum.player_pos if game.asylum else (0, 0),
            "goals_completed": game.asylum.goals_completed if game.asylum else False
        } if game.asylum else None,
        "hero_upgrade_level": game.hero_upgrade_level,
        "shop_pool": [h.__dict__ for h in game.shop_pool]
    }
    with open(filename, 'w') as f:
        json.dump(data, f, default=str)

def load_game(game, filename="save.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        game.party = [Hero(h["name"], h["psyche"]) for h in data["party"]]
        for i, h in enumerate(game.party):
            orig = data["party"][i]
            h.hp = orig["hp"]
            h.max_hp = orig["max_hp"]
            h.insanity = orig["insanity"]
            h.attack = orig["attack"]
            h.defense = orig["defense"]
            h.affliction = orig["affliction"]
        game.dead_heroes = [Hero(h["name"], h["psyche"]) for h in data.get("dead_heroes", [])]
        for i, h in enumerate(game.dead_heroes):
            orig = data["dead_heroes"][i]
            h.hp = orig["hp"]
            h.max_hp = orig["max_hp"]
            h.insanity = orig["insanity"]
            h.attack = orig["attack"]
            h.defense = orig["defense"]
            h.affliction = orig["affliction"]
        game.inventory = data["inventory"]
        game.letters_collected = data["letters_collected"]
        game.state = data["state"]
        if data.get("asylum"):
            game.asylum = Asylum(data["asylum"]["level"])
            game.asylum.map = data["asylum"]["map"]
            game.asylum.player_pos = tuple(data["asylum"]["player_pos"])
            game.asylum.goals_completed = data["asylum"]["goals_completed"]
        game.hero_upgrade_level = data.get("hero_upgrade_level", 0)
        game.shop_pool = [Hero(h["name"], h["psyche"]) for h in data.get("shop_pool", [])]
        for i, h in enumerate(game.shop_pool):
            orig = data["shop_pool"][i]
            h.hp = orig["hp"]
            h.max_hp = orig["max_hp"]
            h.insanity = orig["insanity"]
            h.attack = orig["attack"]
            h.defense = orig["defense"]
            h.affliction = orig["affliction"]
    except FileNotFoundError:
        pass