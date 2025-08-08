import pygame
import random
from hero import Hero
from enemy import Enemy
from asylum import Asylum
from save import save_game, load_game

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "sanctuary" # States: sanctuary (safe hub outside asylum), ward (exploration), therapy(combat)
        self.party = [] # List of heros in current party
        self.dead_heros = [] # List of dead inmates
        self.inventory = {"sedatives": 10, "keys": 5, "gold": 0}
        self.letters_collected = [] # List of love letters (story progression items)
        self.asylum = None
        self.enemies = []
        self.is_boss_fight = False
        self.selected_hero = 0 # For combat selection
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.turn_queue = [] # Simple queue-based turn management
        self.message = "" # For displaying event messages
        self.hero_upgrade_level = 0 # For sanctuary upgrades
        self.shop_pool = []
        self.hero_cost = 10
        self.generate_reception_pool()
        self.selected_building = None # For Sanctuary buildings
        self.buildings = {
            "reception": False, # Recruitment
            "chapel": False,    # Insanity relief
            "pharmacy": False,  # Insanity relief with risk
            "tool_shed": False, # Gear upgrades
            "schizophrenic_whisperer": False, # Skill upgrades
            "ghost_merchant": False, # Trinkets
            "lobotomy_tent": False,   # Treat Afflictions
            "wounded_attendant": False, # Buffs
            "memorial_garden": False, # View dead
            "letter_archive": False    # View letters
        }
        self.trinkets = ["Heart Shaped Locket", "Ring of Passion", "Cloak of Regrets"]  # Add more
        self.trinket_cost = 50


"""
Methods for Sanctuary buildings and functions
"""

    def generate_reception_pool(self):
        self.reception_pool = []
        for i in range(3):
            pysches = ["Delusion", "Hysteria", "Obsession", "Phobia"]
            psyche = random.choice(psyches)
            hero = Hero(f"Echo {random.randint(1, 100)}", psyche)
            hero.attack += self.hero_upgrade_level          # Consider making this more modular
            hero.defense += self.hero_upgrade_level // 2
            self.reception_pool.append(hero)

    def upgrade_heros(self):
        if self.inventory["keys"] > 0:
            self.inventory["keys"] -= 1
            self.hero_upgrade_level += 1
            self.message = f"Upgraded Sanctuary to level {hero_upgrade_level}. Future Inmates will recruit stronger."
        else:
            self.message = "Not enough keys to upgrade."

    def open_building(self, building):
        if self.selected_building:
            self.selected_building = None
        else:
            self.selected_building = building
        self.message = f"{self.get_building_name(building)} " + ("entered." if self.selected_building else "left.")

    def get_building_name(self, building):
        names = {
            "reception": "Reception",
            "chapel": "Chapel",
            "pharmacy": "Pharmacy",
            "tool_shed": "Tool Shed",
            "schizophrenic_whisperer": "Schizophrenic Whisperer",
            "ghost_merchant": "Ghost Merchant",
            "lobotomy_tent": "Lobotomy Tent",
            "wounded_attendant": "Wounded Attendant",
            "memorial_garden": "Memorial Garden",
            "letter_archive": "Love Letter Archive"
        }
        return names.get(building, building.capitalize())

    def chapel_insanity_relief(self):
        if self.inventory["gold"] >= 20:
            self.inventory["gold"] -= 20
            for hero in self.party:
                hero.insanity = max(0, hero.insanity - 30)
            self.message = "Chapel: Insanity relieved for 20 gold."
        else:
            self.message = "Not enough gold."
    
    def pharmacy_stress_relief(self):
        if self.inventory["gold"] >= 15:
            self.inventory["gold"] -= 15
            for hero in self.party:
                hero.insanity = max(0, hero.insanity - 25)
                if random.random() < 0.2:
                    hero.affliction = "Heartbroken" if hero.affliction is None else hero.affliction
            self.message = "Pharmacy: Curiously colored pills restore the party's insanity. But at what cost?"
        else:
            self.message = "Not enough gold."
    
    def tool_shed_upgrade(self, hero_index):
        if 0 <= hero_index < len(self.party) and self.inventory["gold"] >= 50:
            self.inventory["gold"] -= 50
            hero = self.party[hero_index]
            hero.attack += 1
            hero.defense += 1
            self.message = f"Tool Shed: Upgraded {hero.name}'s belongings for 50 gold."
        else:
            self.message = "Invalid inmate or not enough gold."
            
    def schizophrenic_whisperer_upgrade(self, hero_index):
        if 0 <= hero_index < len(self.party) and self.inventory["gold"] >= 40:
            self.inventory["gold"] -= 40
            hero = self.party[hero_index]
            hero.max_hp += 5
            hero.hp += 5
            self.message = f"Schizophrenic Whisperer: {hero.name} listened to the ramblings and gained constitution for 40 gold."
        else:
            self.message = "Invalid inmate or not enough gold."
    
    def buy_from_merchant(self, trinket_index):
        if 0 <= trinket_index < len(self.trinkets) and self.inventory["gold"] >= self.trinket_cost:
            self.inventory["gold"] -= self.trinket_cost
            trinket = self.trinkets[trinket_index]
            if self.party:
                hero = self.party[0]
                if trinket == "Heart Shaped Locket":
                    hero.max_hp += 10
                    hero.hp += 10
                elif trinket == "Ring of Passion":
                    hero.attack += 3
                elif trinket == "Cloak of Regrets":
                    hero.defense += 2
                self.message = f"Ghost Merchant: Bought {trinket} for {self.trinket_cost} gold. In the pockets of {hero.name}."
            else:
                self.message = "Invalid trinket or not enough gold."
    
    def lobotomy_treatment(self, hero_index):
        if 0 <= hero_index < len(self.party) and self.inventory["gold"] >= 30:
            self.inventory["gold"] -= 30
            hero = self.party[hero_index]
            hero.affliction = None
            self.message = f"Lobotomy Tent: Cured {hero.name}'s afflictions for 30 gold."
        else:
            self.message = "Invalid inmate or not enough gold."

    def attendant_buff(self):
        if self.inventory["gold"] >= 25:
            self.inventory["gold"] -= 25
            for hero in self.party:
                hero.defense += 1
            self.message = "Wounded Attendant: Taught your party better coping mechanisms, +1 defense to inmates for 25 gold."
        else:
            self.message = "Not enough gold."

    def enter_asylum(self):
        if len(self.party) == 0:
            self.message = "You need to recruit more inmates to the party."
            return
        if self.asylum is None:
            self.asylum = Asylum(1) # Start at level 1
        self.state = "ward"
        self.message = f"Entered {self.asylum.theme}."


"""
Event methods for battles.

Currently the queue goes through dead enemies ... CHANGE THIS with checks to skip dead enemies/heros
"""
    
    def handle_event(self, event_type):
        
        # Normal Battle 
        if event_type == "start_therapy":
            num_enemies = random.randint(2, 4)
            enemy_name = f"{self.asylum.theme} Phantom" # Add more creative names later
            self.enemies = [Enemy(enemy_name, self.asylum.level) for _ in range(num_enemies)]
            self.state = "therapy"
            self.is_boss_fight = False
            self.turn_queue = self.party + self.enemies # Alternating turns between the party and enemies
            random.shuffle(self.turn_queue) # Add some randomness to the turn order
            self.message = "Therapy session begins!"

        # Boss Battle
        elif event_type == "start_boss":
            boss_name = f"Boss of {self.asylum.theme}" # Add more creative names later
            self.enemies = [Enemy(boss_name, self.asylum.level * 2, is_boss=True)]
            self.state = "therapy"
            self.is_boss_fight = True
            self.turn_queue = self.party + self.enemies
            random.shuffle(self.turn_queue)
            self.message = f"{boss_name} awakened!"

        # Letter Found    
        elif event_type == "found_letter":
            letter = f"Letter {len(self.letters_collected) + 1}"
            self.letters_collected.append(letter)
            self.message = f"Found {letter}: 'My beloved, the doctors can't keep us apart...'"
            # Buff party
            for hero in self.party:
                hero.max_hp += 2
                hero.hp = min(hero.hp + 2, hero.max_hp)
        
        # Stepped On Trap
        elif event_type == "trigger_trap":
            for hero in self.party:
                hero.add_insanity(20)
            self.messsage = "Shock trap! Insanity rises."

       # Hallucinations 
        elif event_type == "hallucination":
            if random.random() < 0.5:
                for hero in self.party:
                    hero.add_insanity(-10) # Reduce insanity
                self.message = "Soothing memories calm the soul."
            else:
                self.enemies = [Enemy("Halucinated Lover", self.asylum.level)] # Add more creative name later
                self.state = "therapy"
                self.is_boss_fight = False
                self.message = "The hallucination attacks the party!"
        
        # Found Key
        elif event_type == "found_key":
            self.asylum.goals_completed = True
            self.message = "Found ward key! Boss room unlocked."

    # Combat Ended
    def check_combat_end(self):
        # Party Wins
        if all(e.hp <= 0 for e in self.enemies):
            
            # Boss Fight
            if self.is_boss_fight:
                self.message = "Ward boss defeated! Advancing to next ward."
                self.inventory["gold"] += 20
                self.Asylum = Asylum(self.asylum.level + 1)
                self.state = "ward"
                self.is_boss_fight = False
                if self.asylum.level > 5:
                    self.check_ending()
            
            # Normal Battle
            else:
                self.state = "ward"
                rewards = {"Sedatives": random.randint(1,3), "keys": random.randint(1,2), "gold": random.randint(5, 15)}
                for item, amt in rewards.items():
                    self.inventory[item] = self.inventory.get(item, 0) + amt
                self.message "Therapy won! Gained rewards."
                
                # 30% chance to find a letter at the end of combat. This needs to be changed in order to allow for full game completion before the game ends.
                if random.random() < 0.3:
                    self.handle_event("found_letter")
            return True

        # Party Wiped
        if all(h.hp <= 0 for h in self.party):
            self.message = "Party wiped! You flee back to Sanctuary."
            self.dead_heros.extend(self.party)
            self.state = "sanctuary"
            self.party = []
            self.generate_reception_pool()
            
            # Reset Level
            if self.asylum:
                self asylum.player_pos = (0, 0)
                # Reset Boss Position
                if self.is_boss_fight:
                    boss_y, boss_x = 4, 4
                    self.asylum.map[boss_y][boss_x] = "boss_room"
            self.is_boss_fight = False
            return True
        return False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state = "sanctuary":
                building_keys = {
                    pygame.K_1: "reception",
                    pygame.K_2: "chapel",
                    pygame.K_3: "pharmacy",
                    pygame.K_4: "tool_shed",
                    pygame.K_5: "schizophrenic_whisperer",
                    pygame.K_6: "ghost_merchant",
                    pygame.K_7: "lobotomy_tent",
                    pygame.K_8: "memorial_garden",
                    pygame.K_9: "letter_archive"
                }
                if event.key in building_keys:
                    self.open_building(building_keys[event.key])
                
                # Reception
                elif self.selected_building == "reception":
                    keys = [pygame.K_a, pygame.K_b, pygame.K_c]
                    if event.key in keys and len(self.reception_pool) >= (keys.index(event.key) + 1):
                        index = keys.index(event.key)
                        if self.inventory["gold"] >= self.hero_cost and len(self.party) < 4:
                            hero = self.reception_pool.pop(index)
                            self.party.append(hero)
                            self.inventory["gold"] -= self.hero_cost
                            self.message = f"{hero.name} joined the party for {self.hero_cost} gold."
                        else:
                            self.message = "Not enough gold or party full."
                    elif event.key == pygame.K_r and self.inventory["gold"] >= 5:
                        self.inventory["gold"] -= 5
                        self.generate_reception_pool()
                        self.message = "New inmates have arrived at the reception for 5 gold."
                
                # Chapel
                elif self.selected_building == "chapel":
                    if event.key == pygame.K_r:
                        self.chapel_insanity_relief()
                
                # Pharmacy
                elif self.selected_building == "pharmacy":
                    if event.key == pygame.K_r:
                        self.pharmacy_stress_relief()
                
                # Tool Shed
                elif self.selected_building == "tool_shed":
                    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                    if event.key in keys and len(self.party) >= (keys.index(event.key) + 1):
                        index = keys.index(event.key)
                        self.tool_shed_upgrade(index)

                # Schizophrenic Whisperer
                elif self.selected_building == "schizophrenic_whisperer":
                    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                    if event.key in keys and len(self.party) >= (keys.index(event.key) + 1):
                        index = keys.index(event.key)
                        self.schizophrenic_whisperer_upgrade(index)
                
                # Ghost Merchant
                elif self.selected_building == "ghost_merchant":
                    keys = [pygame.K_1, pygame.K_2, pygame.K_3]
                    if event.key in keys and len(self.trinkets) >= (keys.index(event.key) + 1):  # Check this logic later if needed
                        index = keys.index(event.key)
                        self.buy_from_merchant(index)
                
                # Lobotomy Tent
                elif self.selected_building == "lobotomy_tent":
                    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                    if event.key in keys and len(self.party) >= (keys.index(event.key) + 1):
                        index = keys.index(event.key)
                        self.lobotomy_treatment(index)

                # Wounded Attendant
                elif self.selected_building == "wounded_attendant":
                    if event.key == pygame.K_r:
                        self.attendant_buff()

                # Memorial Garden
                elif self.selected_building == "memorial_garden":
                    pass  # View only
                
                # Letter Archive
                elif self.selected_building == "letter_archive":
                    pass  # View letters
                
                # Enter Asylum
                if event.key == pygame.K_e and not self.selected_building:
                    self.enter_asylum()
                
                # Sanctuary Upgrades
                elif event.key == pygame.K_u and not self.selected_building:
                    self.upgrade_heros()
                

"""
Event methods for Wards
"""
            elif self.state == "ward":
                
                # Party Movement Out Of Combat
                directions = {
                    pygame.K_UP: (0, -1),
                    pygame.K_DOWN: (0, 1),
                    pygame.K_LEFT: (-1, 0),
                    pygame.K_RIGHT: (1, 0)
                }
                if event.key in directions:
                    dx, dy = directions[event.key]
                    new_x = self.asylum.player_pos[0] + dx
                    new_y = self.asylum.player_pos[1] + dy
                    width = len(self.asylum.map[0])
                    height = len(self.asylum.map)
                    if 0 <= new_x < width and 0 <= new_y < height:
                        self.asylum.player_pos = (new_x, new_y)
                        room = self.asylum.map[new_y][new_x]

                        # Boss Room
                        if room == "boss_room":
                            if self.asylum.goals_completed:
                                event_type = "start_boss"
                            else:
                                self.message = "Boss room locked. Find the key to enter."
                                event_type = None
                        
                        # Key room
                        elif room == "key":
                            event_type = "found_key"
                        
                        # Other Room
                        else:
                            event_type = room if room != "empty" and room != "boss_room" else None
                        
                        # Handle Events
                        if event_type:
                            self.handle_event(event_type)
                        
                        # All rooms other than boss room start as empty rooms
                        if room != "boss_room":
                            self.asylum.map[new_y][new_x] = "empty"
            
"""
Battle Events
"""
            elif self.state == "therapy":

                # Attack
                if event.key == pygame.K_a:  
                    if self.turn_queue and isinstance(self.turn_queue[0], Hero):
                        hero = self.turn_queue[0]
                        if self.enemies:
                            target = self.enemies[0]  # Always targets the first enemy. Change this for manual selection later.
                            damage = max(0, hero.attack - (target.defense if hasattr(target, 'defense') else 0))
                            target.hp -= damage
                            self.message = f"{hero.name} attacks {target.name} for {damage} damage."
                            
                            # Paranoia Effect
                            if hero.affliction == "Paranoia" and random.random() < 0.3:
                                ally = random.choice(self.party)
                                if ally != hero:
                                    ally.take_damage(hero.attack // 2)
                                    self.message += " (Paranoia: Hits ally!)"
                            
                            # Next Turn
                            self.turn_queue.pop(0)

                # Heal
                elif event.key == pygame.K_h:
                    if self.turn_queue and isinstance(self.turn_queue[0], Hero):
                        hero = self.turn_queue[0]
                        for h in self.party:
                            h.hp = min(h.max_hp, h_hp + 5)
                            h.add_insanity(-5)
                        self.message = f"{hero.name} calms the party."
                        self.turn_queue.pop(0)

                # Switch Selected Heros
                elif event.key == pygame.K_SPACE:
                    self.selected_hero = (self.selected_hero + 1) % len(self.party)


            # Save Gamestates
            if event.key == pygame.K_s and self.state != "sanctuary":
                save_game(self)
                self.message = "Game saved."

            # Load Gamestates
            elif event.key == pygame.K_l:
                load_game(self)
                self.message = "Game loaded from previous save point."

            # Return to Sanctuary
            elif event.key == pygame.K_q:
                if self.state != "sanctuary":
                    self.state = "sanctuary"
                    self.generate_reception_pool()
                    self.message = "Retreated to the Sanctuary."

    # Update Gamestates
    def update(self):

        # Battle States
        if self.state == "therapy":
            if self.turn_queue:
                current = self.turn_queue[0]
                 
                 # Handle Enemy Turns
                 if isinstance(current, Enemy) and current.hp > 0:
                    if self.party:
                        target = random.choice([h for h in self.party if h.hp > 0])  # Enemies attack a random party member. Change this later with better targetting logic
                        current.act(target)
                        self.message = f"{current.name} attacks {target.name}."
                    self.turn_queue.pop(0)

            # Shuffle Turns
            else:
                self.turn_queue = [e for e in self.party + self.enemies if e.hp > 0]
                random.shuffle(self.turn_queue)
            self.check_combat_end()

        # 10% chance to add insanity when in Wards
        if self.state == "ward" and random.random() < 0.1:
            for hero in self.party:
                hero.add_insanity(5)
        
        # Check for Game End
        if len(self.letters_collected) >= 10:
            self.check_ending()

"""
Game end
"""    

    # On Game End
    def check_ending(self):
        
        # If player has collected all of the letters
        if len(self.letters_collected) >= 10:
            self.message = "All letters have been collected! Your party escapes from madness."
        
        # If player quits before collecting all of the letters
        else:
            self.message = "Incomplete collection: Permanent commitment to Love Letter Asylum."
        
        # Reset to game start
        self.state = "sanctuary"
        self.party = []
        self.inventory = ["sedatives": 10, "keys": 5, "gold": 0]
        self.letters_collected = []
        self.asylum = None
        self.hero_upgrade_level = 0
        self.generate_reception_pool()
        self.dead_heros = []

"""
Draw game objects on screen 

THIS SECTION NEEDS CHANGING WHEN ART IS ADDED
"""    
    def draw(self):
        # screen background is all black
        self.screen.fill((0, 0, 0))

        # Draw the sanctuary
        if self.state == "sanctuary":
            
            # Drawing the selected building
            if self.selected_building:
                building_name = self.get_building_name(self.selected_building)
                text = self.font.render(f"{building_name} - Close with same keypress", True, (255, 255, 255))
                # Display the name of the building
                self.screen.blit(text, (10, 10))
                
                # Reception
                if self.selected_building == "reception":
                    for i, hero in enumerate(self.shop_pool):
                        hero_text = self.small_font.render(f"A/B/C: {hero.name}({hero.psyche}) - Cost: {Self.hero_cost} gold", True, (255, 255, 255))
                        # Display recruitable inmates
                        self.screen.blit(hero_text, (10, 50 + i * 30))
                    refresh_text = self.small_font.render("R: Refresh (5 gold)", True, (255, 255, 255))
                    # Display refresh cost
                    self.screen.blit(refresh_text, (10, 50 + len(self.shop_pool) * 30))
                
                # Chapel
                elif self.selected_building == "chapel":
                    text = self.small_font.render("R: Relieve insanity (20 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                
                # Pharmacy
                elif self.selected_building == "pharmacy":
                    text = self.small_font.render("R: Relive insanity with risk (15 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                
                # Tool Shed
                elif self.selected_building == "tool_shed":
                    text = self.small_font.render("1-4: Upgrade inmate gear (50 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, hero in enumerate(self.party):
                        hero_text = self.small_font.render(f"{i+1}: {hero.name}", True, (255, 255, 255))
                        self.screen.blit(hero_text, (10, 80 + i * 30))
                
                # Schizophrenic Whisperer
                elif self.selected_building == "schizophrenic_whisperer":
                    text = self.small_font.render("1-4: Upgrade inmate skills (40 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, hero in enumerate(self.party):
                        hero_text = self.small_font.render(f"{i+1}: {hero.name}", True, (255, 255, 255))
                        self.screen.blit(hero_text, (10, 80 + i * 30))
                
                # Ghost Merchant
                elif self.selected_building == "ghost_merchant":
                    text = self.small_font.render("1-3: Buy trinket (50 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, trinket in enumerate(self.trinkets):
                        trinket_text = self.small_font.render(f"{i+1}: {trinket}", True, (255, 255, 255))
                        self.screen.blit(trinket_text, (10, 80 + i * 30))
                
                # Lobotomy Tent
                elif self.selected_building == "lobotomy_tent":
                    text = self.small_font.render("1-4: Cure affliction (30 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, hero in enumerate(self.party):
                        hero_text = self.small_font.render(f"{i+1}: {hero.name}({hero.affliction or 'None'})", True, (255, 255, 255))
                        self.screen.blit(hero_text, (10, 80 + i * 30))

                # Wounded Attendant:
                elif self.selected_building == "wounded_attendant":
                    text = self.small_font.render("R: Teach the party coping mechanisms (+1 def to all members, 25 gold)", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                
                # Memorial Garden:
                elif self.selected_building == "memorial_garden":
                    text = self.small_font.render("Memorial Garden: Beloved fallen inmates lie here.", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, hero in enumerate(self.dead_heros):
                        hero_text = self.small_font.render(f"{hero.name}{hero.psyche}", True, (255, 255, 255))
                        self.screen.blit(hero_text, (10, 80 + i * 30))
                
                # Love Letter Archive
                elif self.selected_building == "letter_archive":
                    text = self.small_font.render("Love Letter Archive", True, (255, 255, 255))
                    self.screen.blit(text, (10, 50))
                    for i, letter in enumerate(self.letters_collected):
                        letter_text = self.small_font.render(letter, True, (255, 255, 255))  # This needs to be changed with the addition of specific love letters
                        self.screen.blit(letter_text, (10, 80 + i * 30))
            
            # Display building names and hotkeys
            else:
                text = self.small_font.render("Sanctuary - 1: Reception, 2: Chapel, 3: Pharmacy, 4: Tool Shed, 5: Schizophrenic Whisperer", True, (255, 255, 255))
                self.screen.blit(text, (10, 10))
                text2 = self.small_font.render("6: Ghost Merchant, 7: Lobotomy Tent, 8: Wounded Attendant, 9: Memorial Garden, 0: Love Letter Archive, E: Enter Asylum, U: Asylum upgrade (1 key)", True, (255, 255, 255))
                self.screen.blit(text2, (10, 50))
            
            # Display party info
            y_offset = 100 if self.selected_building else 100
            for i, hero in enumerate(self.party):
                hero_text = self.small_font.render(f"{hero.name}({hero.psyche}): HP {hero.hp}/{hero.max_hp}, Ins {hero.insanity},  Aff {hero.affliction or None}", True, (255, 255, 255))
                self.screen.blit(hero_text, (10, y_offset + i * 30))
            
            # Display Party Inventory
            Inv_text = self.small_font.render(f"Inventory: Sedatives {self.inventory['sedatives']}, Keys {self.inventory['keys']}, Gold {self.inventory['gold']}", True, (255, 255, 255))
            self.screen.blit(Inv_text, (10, y_offset + len(self.party) * 30  + 20))

            # Display number of letters collected
            letters_text = self.small_font.render(f"Letters: {len(self.letters_collected)}/10", True, (255,255, 255))
            self.screen.blit(letters_text, (10, y_offset + len(self.party) * 30 + 50))

            # Display Sanctuary level
            upgrade_text = self.small_font.render(f"Sanctuary_Level: {self.hero_upgrade_level}", True, (255, 255, 255))
            self.screen.blit(upgrade_text, (10, y_offset + len(self.party) * 30 + 80))
        

"""
Draw Exploration Screens in Asylum's Wards
"""

        elif self.state == "Ward":

            # Ward name/info
            theme_text = self.font.render(f"{self.asylum.theme} - Level {self.asylum.level}", True, (255, 255, 255))
            self.screen.blit(theme_text, (10, 10))
            goal_text = self.small_font.render("Goal: Find the ward key to unlock the ward boss' chambers. Defeat them to proceed to the next floor.", True, (255, 255, 255))
            self.screen.blit(goal_text, (10, 50))
            
            # Drawing the map
            cell_size = 50
            for y in range(len(self.asylum.map)):
                for x in range(len(self.asylum.map[0])):
                    color = (100, 100, 100) if self.asylum.map[y][x] == "empty" else (255, 0, 0) if self.asylum.map[y][x] == "boss_room" else (0, 255, 0) if self.asylum.map[y][x] == "key" else (200, 200, 200)
                    pygame.draw.rect(self.screen, color, (100 + x * cell_size, ,100 + y * cell_size, cell_size, cell_size))
                # Draw the player on the map
                pygame.draw.circle(self.screen, (0, 255, 0), (100 + self.asylum.player_pos[0] * cell_size + 25, 100 + self.asylum.player_pos[1] * cell_size + 25), 20)


"""
Draw the combat scenes (therapy sessions)
"""

        elif self.state == "therapy":
            text = self.font.render("Therapy Session! - A to attack, H to heal, Space to select", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))

            # Display inmates and selection
            for i, hero in enumerate(self.party):
                hero_color = (0, 255, 0) if i == self.selected_hero else (255, 255, 255)
                hero_text = self.small_font.render(f"{hero.name}: HP {hero.hp}/{hero.max_hp}, Ins {hero.insanity}", True, hero_color)
                self.screen.blit(hero_text, (10, 50 + i * 30))
            
            # Display enemies
            for i, enemy in enumerate(self.enemies):
                if enemy.hp > 0:
                    enemy_text = self.small_font.render(f"{enemy.name}: HP {enemy.hp}", True, (255, 0, 0))
                    self.screen.blit(enemy_text, (400, 50 + i * 30))

 """
 UI Event Message Display
 """      

        # Display UI messages
        msg_text = self.small_font.render(self.message, True, (255, 255, 0))
        self.screen.blit(msg_text, (10, 550))
