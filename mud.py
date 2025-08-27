import time
import random
import json
import text
import sys
import select
import os
import math

class Game:
    """
    Class constructor for Game
    """
    def __init__(self):
        self.game_state = ''
        self.maze = None
        self.storage = Storage()
        self.player = None

    def set_state(self, state):
        self.game_state = state
    
    def get_state(self):
        return self.game_state
    
    def get_maze(self):
        return self.maze
 
    def get_options(self):
        if self.game_state == 'start':
            choices = text.start_choices
            return choices
        elif self.game_state == 'travel':
            choices = self.maze.room_options()
            if type(self.maze.current_room) == MonsterRoom:
                if self.maze.current_room.claimed == False:
                    choices.insert(0, 'Fight monster')
            elif type(self.maze.current_room) == TreasureRoom:
                if self.maze.current_room.claimed == False:
                    choices.insert(0, 'Open chest')
            elif type(self.maze.current_room) == BossRoom:
                if self.maze.current_room.claimed == False:
                    choices.insert(0, 'Challenge the boss')
            elif type(self.maze.current_room) == Room:
                return choices
            choices.append('View inventory')
            choices.append('Quit')

            return choices
        elif self.game_state == 'item chest':
            choices = ['Equip item', 'Go back']
            return choices
        elif self.game_state == 'consumable chest':
            choices = ['Consume item', 'Go back']
            return choices
        elif self.game_state == 'inventory':
            choices = []
            choices.append('Use item')
            choices.append('Go back')
            return choices
        elif self.game_state == 'boss':
            choices = ['Fight boss', 'Go back']
            return choices
        
    def prompt_player_choice(self, choices):
        for i, opt in enumerate(choices):
            print(f'{(i + 1)}. {opt}')
            time.sleep(0.05)
        
        while True:
            _input = input(text.input_prompt).strip()
            
            if not _input:
                print("Please enter a valid choice.")
                for i, opt in enumerate(choices):
                    print(f'{(i + 1)}. {opt}')
                    time.sleep(0.05)
                continue
            
            if _input in choices:
                return _input
            
            if _input.isdigit():
                choice_num = int(_input)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
            
            print("Please type out a valid option or number.")
            for i, opt in enumerate(choices):
                print(f'{(i + 1)}. {opt}')
                time.sleep(0.05)
            continue

    def start_game(self):
        rooms = []
        rooms.append(Room(0))
        for i in range(1, text.maze_size):
            if i % 2 == 0:
                room = MonsterRoom((i + 1), text.Monsters.keys())
                room.generateMonster()
                room.generateDrops()
                rooms.append(room)
            elif i % 2 == 1:
                rooms.append(TreasureRoom(i + 1))
            else:
                rooms.append(Room(i + 1))
        rooms.append(BossRoom(text.maze_size + 1))
        self.maze = Maze(rooms, rooms[0])
        self.maze.generate_maze()
        self.create_player()
        print(text.printing_text_large_spacing)
        self.pretty_print(text.started_text)
        input()
        self.maze.draw_rooms()
        self.set_state('travel')

    def pretty_print(self, text):
        i = 0
        while i < len(text):
            if select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline()

                sys.stdout.write(text[i:]) 
                # sys.stdout.flush()
                
                break
            sys.stdout.write(text[i])
            sys.stdout.flush()
            time.sleep(0.032)
            i += 1

    def quit_game(self):
        sys.exit()

    def welcome(self):
        print(text.welcome_prompt)
        choices = self.get_options()
        chosen = False
        while chosen == False:
            choice = self.prompt_player_choice(choices)
            if choice not in choices and choice not in ['1', '2', '3']:
                print('Please type out a valid option')
            elif choice == 'start' or choice == '1':
                chosen = True
                self.start_game()
            elif choice == 'quit' or choice == '2':
                chosen = True
                self.quit_game()

    def create_player(self):
        stats = Stats(text.default_health, text.default_attack)
        self.player = Player(stats)
        self.player.create_new_storage(self.storage, text.player_save_file)

    def get_player(self):
        return self.player

    def load_data(self):
        pass

    def save_all_data(self, file):    
        self.storage.save_data(file, {
            "Room_id": self.maze.current_room.id
        })
        self.player.save_to_storage(self.storage, file)

class Storage:
    def __init__(self):
        pass
        
    def get_data(self, file) -> dict:
        if not os.path.exists(file):
            return {}
        with open(file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
            
    def save_data(self, file, obj) -> None:
        data = self.get_data(file)

        if isinstance(data, dict) and isinstance(obj, dict):
            data.update(obj)
        elif isinstance(data, list) and isinstance(obj, list):
            data.extend(obj)
        else:
            data = obj 

        # save back
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

#List of things we need to do
#Create maze
class Maze:
    """
    Class constructor for Maze
    """
    def __init__(self, rooms: list['Room'], starting_room):
        """
        Takes in a dict of Room objects and a starting room.
        """
        self.rooms = rooms
        self.starting_room = starting_room
        self.current_room = starting_room

    def generate_maze(self):
        num_cols = 3
        regular_rooms = self.rooms[:-1]
        
        for i, room in enumerate(regular_rooms):
            row = i // num_cols
            col = i % num_cols
            
            if col < num_cols - 1 and (i + 1) < len(regular_rooms):
                right_room = regular_rooms[i + 1]
                room.connection(right_room, 'right')
                right_room.connection(room, 'left')
            
            num_rows = (len(regular_rooms) + num_cols - 1) // num_cols
            if row < num_rows - 1 and (i + num_cols) < len(regular_rooms):
                down_room = regular_rooms[i + num_cols]
                room.connection(down_room, 'down')
                down_room.connection(room, 'up')
        
        boss_room = self.rooms[-1]
        last_regular_room = regular_rooms[-1]
        boss_room.connection(last_regular_room, 'up')
        last_regular_room.connection(boss_room, 'down')
    
    def get_room_key(self, room):
        # Convert room objects to boolean values
        up = room.connects['up'] is not None
        down = room.connects['down'] is not None
        left = room.connects['left'] is not None
        right = room.connects['right'] is not None

        if isinstance(room, BossRoom):
            return "BOSS_CLEAN"

        if up and down and left and right: return "NSEW"

        if up and down and left and not right: return "NSW"
        if up and down and not left and right: return "NSE"
        if up and not down and left and right: return "NEW"
        if not up and down and left and right: return "SEW"

        if up and down and not left and not right: return "NS"
        if not up and not down and left and right: return "EW"
        if up and not down and left and not right: return "NW"
        if up and not down and not left and right: return "NE"
        if not up and down and left and not right: return "SW"
        if not up and down and not left and right: return "SE"

        if up and not down and not left and not right: return "N"
        if not up and down and not left and not right: return "S"
        if not up and not down and left and not right: return "W"
        if not up and not down and not left and right: return "E"
        return "BOSS"

    def draw_rooms(self):
        row_chunks = []
        rooms_per_row = 3
        
        regular_rooms = self.rooms[:-1]  # Exclude boss room
        
        # Draw regular rooms in grid
        for row_start in range(0, len(regular_rooms), rooms_per_row):
            row_rooms = regular_rooms[row_start:row_start + rooms_per_row]
            
            row_arts = []
            for room in row_rooms:
                if room.id == self.current_room.id:
                    room_art = text.player_rooms[self.get_room_key(room)]
                else:
                    room_art = text.rooms[self.get_room_key(room)]
                row_arts.append(room_art)
            
            if not row_arts:
                continue
                
            max_height = max(len(art.strip("\n").splitlines()) for art in row_arts)
            max_width = max(max(len(line) for line in art.strip("\n").splitlines()) for art in row_arts)
            
            row_chunk = [[] for _ in range(max_height)]
            
            for art in row_arts:
                lines = art.strip("\n").splitlines()
                lines = [line.ljust(max_width) for line in lines]
                
                while len(lines) < max_height:
                    lines.append(" " * max_width)
                
                for i, line in enumerate(lines):
                    row_chunk[i].append(line)
            
            row_chunks.append(row_chunk)
        
        # Print regular maze
        map_str = ""
        for row in row_chunks:
            for line in row:
                map_str += "".join(line) + "\n"
        
        print(map_str.rstrip("\n"))
        
        # Print boss area separately
        boss_room = self.rooms[-1]
        print("=" * 15)
        if boss_room.id == self.current_room.id:
            print("BOSS CHAMBER (YOU ARE HERE)")
        else:
            print("BOSS CHAMBER")
        print("=" * 15)
        
        if boss_room.id == self.current_room.id:
            boss_art = text.player_rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        else:
            boss_art = text.rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        
        boss_lines = boss_art.strip("\n").splitlines()
        for line in boss_lines:
            print(line.center(14) + '\n')
    
    def room_options(self):
        options = []
        for direction in text.directions:
            connected_room = self.current_room.connects.get(direction)
            if connected_room:
                # Special handling for boss room access
                if isinstance(connected_room, BossRoom):
                    options.append('enter boss chamber')
                else:
                    options.append('go ' + direction)
        return options

    def travel_to(self, direction):
        # Handle special boss room access
        if direction == 'boss chamber' or direction == 'boss':
            # Find if current room connects to boss room
            for dir_key, connected_room in self.current_room.connects.items():
                if isinstance(connected_room, BossRoom):
                    self.current_room = connected_room
                    print("You step through the ominous doorway into the Boss Chamber...")
                    return
            print("You cannot access the Boss Chamber from here.")
            return
        
        # Regular movement
        connected_room = self.current_room.connects.get(direction)
        if connected_room:
            self.current_room = connected_room
            if isinstance(connected_room, BossRoom):
                print("You enter the foreboding Boss Chamber...")
            else:
                print(text.successful_room_travel + str(connected_room.id))

# ROOM CLASSES
class Room:
    """
    Class construtor for Room
    For each room in the str_chain, it:

    Prints the room's .connects attribute (presumably a dictionary or list of connected rooms by direction)

    Then prints out the IDs of connected rooms, assuming each room has an id attribute.
    """
    def __init__(self, id: int):
        self.id = id
        self.connects = {'up': None, 'left': None, 'right': None, 'down': None}

    def connection(self, room, direction):
        if direction in self.connects:
            self.connects[direction] = room

class TreasureRoom(Room):
    def __init__(self, _id):
        super().__init__(_id)
        self.claimed = False
        if _id < 5:
            drop = Drop(text.weaponweights5, text.armourweights5)
            self.drop = drop.generateDrop()
        elif _id < 10:
            drop = Drop(text.weaponweights10, text.armourweights10)
            self.drop = drop.generateDrop()
        elif _id < 15:
            drop = Drop(text.weaponweights15, text.armourweights15)
            self.drop = drop.generateDrop()
        elif _id < 20: 
            drop = Drop(text.weaponweights20, text.armourweights20)
            self.drop = drop.generateDrop()
        else:
            drop = Drop(text.weaponweights25, text.armourweights25)
            self.drop = drop.generateDrop()

    def get_drops(self):
        """
        Returns the items that are contained in the treasure room.
        """
        return self.drop.drop

    def get_type(self):
        """
        Returns the type of item that is contained in the treasure room.
        """
        return self.drop.type

class MonsterRoom(Room):
    def __init__(self, id: int, availableMonsters: list):
        super().__init__(id)
        self.monster = ''
        self.availableMonsters = availableMonsters
        self.claimed = False

    def generateMonster(self):
        """
        Returns the randomly generated monster in the room.
        Temporary function until better system is found.
        """
        if len(self.availableMonsters) == 0:
            return 'list of monsters is empty'
        if id == 0:
            i = 0
        else:
            i = random.randint(0, self.id//2)
        self.monster = list(self.availableMonsters)[i]
    
    def generateDrops(self):
        i = random.randint(0, 1)
        if i == 0:
            if self.id < 5:
                drop = Drop(text.weaponweights5, text.armourweights5)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 10:
                drop = Drop(text.weaponweights10, text.armourweights10)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 15:
                drop = Drop(text.weaponweights15, text.armourweights15)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 20: 
                drop = Drop(text.weaponweights20, text.armourweights20)
                drop.generateArmourDrop()
                self.drop = drop
            else:
                drop = Drop(text.weaponweights25, text.armourweights25)
                drop.generateArmourDrop()
                self.drop = drop
        elif i == 1:
            if self.id < 5:
                drop = Drop(text.weaponweights5, text.armourweights5)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 10:
                drop = Drop(text.weaponweights10, text.armourweights10)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 15:
                drop = Drop(text.weaponweights15, text.armourweights15)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 20: 
                drop = Drop(text.weaponweights20, text.armourweights20)
                drop.generateWeaponDrop()
                self.drop = drop
            else:
                drop = Drop(text.weaponweights25, text.armourweights25)
                drop.generateWeaponDrop()
                self.drop = drop

class BossRoom(Room):
    def __init__(self, id: int):
        super().__init__(id)
        self.claimed = False
        self.boss_monster_name = text.boss_monster
        self.boss_monster = Monster(Stats(text.boss_monster_stats[0], text.boss_monster_stats[1]))
    


# CHARACTER CLASSES
class Character:
    def __init__(self, stats):
        self.stats = stats
        self.abilities = []
        for a in text.move_pool:
            self.abilities.append(Ability(a))
        # self.inventory = Inventory() (to be updated)
 
class Player(Character):
    def __init__(self, stats):
        super().__init__(stats)
        self.inventory = None
        self.base_atk = text.default_attack
        self.base_health = text.default_health

    def create_new_storage(self, storage: Storage, file: str):
        default_data = storage.get_data(text.default_save_file)
        storage.save_data(file, default_data)
        self.load_from_storage(storage, file)

    def load_from_storage(self, storage: Storage, file: str):
        data = storage.get_data(file)
        self.stats.max_health = data["Player_max_health"]
        self.stats.current_health = data["Player_current_health"]
        self.stats.attack = data["Player_attack"]
        self.inventory = Inventory(storage, file)

    def save_to_storage(self, storage: Storage, file: str):
        storage.save_data(file, {
            "Player_max_health": self.stats.max_health,
            "Player_current_health": self.stats.current_health,
            "Player_attack": self.stats.attack
        })
        self.inventory.save_inventory()
    
    def show_inventory(self):
        if self.inventory:
            self.inventory.show_inventory()
        else:
            print("No inventory loaded.")
    
    def atk_potion(self, amt):
        self.base_atk += amt
    
    def health_potion(self, amt):
        self.base_health += amt

    def recalculate_stats(self):
        # Reset attack and health back to base
        self.stats.attack = self.base_atk
        old_max_health = self.stats.max_health
        old_current_health = self.stats.current_health

        weapon = self.inventory.items.get("Weapon", None)
        attack_bonus = text.Weapon.get(weapon, 0) if weapon else 0

        armour = self.inventory.items.get("Armour", {})
        defence_bonus = sum(text.Armour.get(part, 0) for part in armour.values() if part)

        self.stats.attack = self.base_atk + attack_bonus
        self.stats.max_health = self.base_health + defence_bonus

        if old_max_health > 0:
            health_ratio = old_current_health / old_max_health
        else:
            health_ratio = 1.0

        self.stats.current_health = round(self.stats.max_health * health_ratio, 1)

        # Ensure it never goes above max
        if self.stats.current_health > self.stats.max_health:
            self.stats.current_health = self.stats.max_health


class Inventory:
    def __init__(self, storage: Storage, file: str):
        self.storage = storage
        self.file = file
        try:
            data = self.storage.get_data(file)
            self.items = data.get("Items", {})
        except FileNotFoundError:
            self.items = {}
            self.save_inventory()  # create file if not exists

    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item and save to JSON."""
        if item_name in text.Consumable.keys():
            if item_name in self.items["Consumables"]:
                self.items["Consumables"][item_name] += quantity
            else:
                self.items["Consumables"][item_name] = quantity
        else:
            if item_name in self.items:
                self.items[item_name] += quantity
            else:
                self.items[item_name] = quantity
        self.save_inventory()

    def use_item(self, item_name: str, quantity: int = 1):
        """Use an item and save to JSON."""
        if item_name not in self.items["Consumables"]:
            print(f"{item_name} not found in inventory.")
            return False
        if self.items["Consumables"][item_name] < quantity:
            print(f"Not enough {item_name} to use.")
            return False
        
        self.items["Consumables"][item_name] -= quantity
        if self.items["Consumables"][item_name] <= 0:
            del self.items["Consumables"][item_name]
        self.save_inventory()
        return True
    
    def equip_weapon(self, weapon_name: str):
        """Equip a weapon to the player, given a weapon name."""
        if weapon_name in text.Weapon.keys():
            self.items["Weapon"] = weapon_name
            print('\n' + text.equip_spacing_text)
            print(f"{weapon_name} has been equipped.")
            print(text.equip_spacing_text + '\n')
            self.save_inventory()
        else:
            print(f"{weapon_name} not found.")
            return False
    
    def equip_armour(self, slot: str, armour_name: str):
        """Equip armour to a given slot."""
        if armour_name in text.Armour:
            if "Armour" not in self.items:
                self.items["Armour"] = {}
            self.items["Armour"][slot] = armour_name
            print('\n' + text.equip_spacing_text)
            print(f"{armour_name} equipped in {slot}.")
            print(text.equip_spacing_text + '\n')
            self.save_inventory()
        else:
            print(f"{armour_name} not found.")
            return False


    def remove_item(self, item_name: str):
        """Remove an item completely."""
        if item_name in self.items:
            del self.items[item_name]
            self.save_inventory()
        else:
            print(f"{item_name} not found in inventory.")

    def save_inventory(self):
        """Save inventory into the JSON file."""
        try:
            data = self.storage.get_data(self.file)
        except FileNotFoundError:
            data = {}
        data["Items"] = self.items
        self.storage.save_data(self.file, data)


    def return_inventory(self):
        if not self.items:
            return "Inventory is empty."

        lines = ["╔═ Inventory ═══════════════╗"]

        # Weapon
        weapon = self.items.get("Weapon", "None")
        lines.append(f"  Weapon       » {weapon}")

        # Armour
        lines.append("  Armour")
        armour = self.items.get("Armour", {})
        for part in ["Helmet", "Chestplate", "Leggings", "Boots"]:
            equipped = armour.get(part, "None")
            lines.append(f"    {part:<11} » {equipped}")

        # Consumables
        lines.append("  Consumables")
        consumables = self.items.get("Consumables", {})
        if consumables:
            for item, qty in consumables.items():
                lines.append(f"    {item:<11} » x{qty}")
        else:
            lines.append("    None")

        lines.append("╚═══════════════════════════╝")

        return "\n".join(lines)

    

class Monster(Character):
    def __init__(self, stats):
        super().__init__(stats)

class Drop():
    def __init__(self, weaponWeights, armourWeights):
        self.weaponWeights = weaponWeights
        self.armourWeights = armourWeights
        self.name = ''
    
    def generateDrop(self):
        r = random.randint(0, 2)
        if r == 0:
            drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
            self.type = 'weapon'
        elif r == 1:
            drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
            self.type = 'armour'
        elif r == 2:
            number = random.randint(1, 3)
            if number == 1:
                drop = 'attack potion'
                self.type = 'consumable'
            elif number == 2:
                drop = 'health potion'
                self.type = 'consumable'
            else:
                drop = 'healing potion'
                self.type = 'consumable'
        self.drop = drop
        return self
    
    def generateArmourDrop(self):
        drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
        self.type = 'armour'
        self.drop = drop
        return self
        
    
    def generateWeaponDrop(self):
        drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
        self.type = 'weapon'
        self.drop = drop
        return self

class Stats:
    def __init__(self, max_health: int, attack: int):
        self.max_health = max_health
        self.attack = attack
        self.current_health = max_health
    
    def take_damage(self, damage):
        if (self.current_health - damage) <= 0:
            self.current_health = 0
            return 'died'
        else:
            self.current_health -= damage
    
    def heal(self, healAmount):
        self.current_health = min(self.current_health + healAmount, self.max_health)
    
    def return_stats(self):
        """Return a formatted string of the player's stats."""
        lines = ["╔═ Player Stats ═════════════╗"]
        lines.append(f"  Health      » {self.current_health}/{self.max_health}")
        lines.append(f"  Attack      » {self.attack}")
        # You can add defense if calculated elsewhere
        lines.append("╚═══════════════════════════╝")
        return "\n".join(lines)


class Ability():
    def __init__(self, name):
        self.name = name
        self.attack = 0
        self.shield = 0
        self.heal = 0
        self.elixir = 1
        self.saved_elixir = 0
        self.magnitude =  0

class CombatSequence():
    def __init__(self, player, monster, base_elixir: int, max_turns: int):
        self.base_elixir = base_elixir
        self.current_turn = 1
        self.max_turns = max_turns

        self.player = player
        self.monster = monster

        self.saved_p = 0 # saved player elixir from each turn
        self.saved_m = 0 # saved monster elixir from each turn
    def _fmt(self, x):
        """Format numbers to 1 decimal if needed, no trailing .0."""
        return int(x) if isinstance(x, (int, float)) and float(x).is_integer() else round(x, 1)


    def start_sequence(self, is_boss=False):
        """
        Compact combat display for normal monsters and bosses in minimal format.
        """
        while self.current_turn <= self.max_turns:
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            print(f"\n===== Turn {self.current_turn} =====\n")
            print(f"Player Health: {self._fmt(self.player.stats.current_health)} | "
                f"{'Boss' if is_boss else 'Monster'} Health: {self._fmt(self.monster.stats.current_health)}")
            print(f"Player Elixir: {p_elixir} | {'Boss' if is_boss else 'Monster'} Elixir: {m_elixir}\n")

            # Choose abilities
            player_seq = self.player_ability_sequence(p_elixir)
            monster_seq = self.monster_ability_sequence(m_elixir)

            # Aggregate totals
            p_total_attack = sum(a.attack for a in player_seq)
            p_total_shield = sum(a.shield for a in player_seq)
            p_total_heal = sum(a.heal for a in player_seq)
            p_total_save = sum(a.saved_elixir for a in player_seq)

            m_total_attack = sum(a.attack for a in monster_seq)
            m_total_shield = sum(a.shield for a in monster_seq)
            m_total_heal = sum(a.heal for a in monster_seq)
            m_total_save = sum(a.saved_elixir for a in monster_seq)

            # Compute damage after shields
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.stats.attack / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.stats.attack / 10))

            # Apply effects
            self.monster.stats.take_damage(dmg_to_monster)
            self.player.stats.take_damage(dmg_to_player)
            self.player.stats.heal(p_total_heal)
            self.monster.stats.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

            # Display turn summary
            player_abilities = []
            if p_total_attack > 0: player_abilities.append(f"Attack {p_total_attack}")
            if p_total_shield > 0: player_abilities.append(f"Shield {p_total_shield}")
            if p_total_heal > 0: player_abilities.append(f"Heal {p_total_heal}")
            if p_total_save > 0: player_abilities.append(f"Save {p_total_save}")

            monster_abilities = []
            if m_total_attack > 0: monster_abilities.append(f"Attack {m_total_attack}")
            if m_total_shield > 0: monster_abilities.append(f"Shield {m_total_shield}")
            if m_total_heal > 0: monster_abilities.append(f"Heal {m_total_heal}")
            if m_total_save > 0: monster_abilities.append(f"Save {m_total_save}")

            print(text.combat_spacing_text)
            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Monster Abilities: {' | '.join(monster_abilities)}\n")

            if dmg_to_player > 0: print(f"Damage to Player: {self._fmt(dmg_to_player)}")
            if dmg_to_monster > 0: print(f"Damage to Monster: {self._fmt(dmg_to_monster)}")
            if p_total_heal > 0: print(f"Player Healed: {self._fmt(p_total_heal)}")
            if m_total_heal > 0: print(f"Monster Healed: {self._fmt(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Monster: {self.saved_m}")
            print(f"Health Status -> Player: {self._fmt(self.player.stats.current_health)} | "
                f"{'Boss' if is_boss else 'Monster'}: {self._fmt(self.monster.stats.current_health)}")

            # Next turn
            input("\nPress Enter to continue...")
            self.current_turn += 1
            os.system('clear')

            if self.player.stats.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.stats.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # End of sequence winner
        if self.player.stats.current_health > self.monster.stats.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'


    def start_boss_sequence(self):
        """
        Boss sequence with elixir steal, shared fate, and minimal, clean display.
        """
        while self.current_turn <= self.max_turns:
            # ===== Calculate elixir =====
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            # ===== Display turn header =====
            print(f"\n===== Turn {self.current_turn} =====\n")
            # ===== Boss steals elixir =====
            steal_amount = random.randint(0, p_elixir // 3)
            p_elixir -= steal_amount
            m_elixir += steal_amount
            if steal_amount > 0:
                print(f"{text.boss_monster} steals {steal_amount} elixir from you!")
            print(f"Player Health: {self._fmt(self.player.stats.current_health)} | Boss Health: {self._fmt(self.monster.stats.current_health)}")
            print(f"Player Elixir: {p_elixir} | Boss Elixir: {m_elixir}\n")

            # ===== Player & Boss choose abilities =====
            player_seq = self.player_ability_sequence(p_elixir)
            monster_seq = self.monster_ability_sequence(m_elixir)

            # ===== Aggregate totals =====
            p_total_attack = sum(a.attack for a in player_seq)
            p_total_shield = sum(a.shield for a in player_seq)
            p_total_heal = sum(a.heal for a in player_seq)
            p_total_save = sum(a.saved_elixir for a in player_seq)

            m_total_attack = sum(a.attack for a in monster_seq)
            m_total_shield = sum(a.shield for a in monster_seq)
            m_total_heal = sum(a.heal for a in monster_seq)
            m_total_save = sum(a.saved_elixir for a in monster_seq)

            # ===== Compute damage with shared fate =====
            shared_fate_percent = 0.25
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.stats.attack / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.stats.attack / 10))

            dmg_to_monster_total = dmg_to_monster * (1 + shared_fate_percent)
            dmg_to_player_total = dmg_to_player * (1 + shared_fate_percent)

            # ===== Apply effects =====
            self.monster.stats.take_damage(dmg_to_monster_total)
            self.player.stats.take_damage(dmg_to_player_total)
            self.player.stats.heal(p_total_heal)
            self.monster.stats.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

            # ===== Special shared fate every 3rd turn =====
            if self.current_turn % 3 == 0:
                self.player.stats.take_damage(dmg_to_monster)
                self.monster.stats.take_damage(dmg_to_player)
                self.monster.stats.heal(p_total_heal)
                self.player.stats.heal(m_total_heal)
                print("Shared Fate Triggered! Effects mirrored this turn.")

            # ===== Minimal display =====
            player_abilities = []
            if p_total_attack > 0: player_abilities.append(f"Attack {p_total_attack}")
            if p_total_shield > 0: player_abilities.append(f"Shield {p_total_shield}")
            if p_total_heal > 0: player_abilities.append(f"Heal {p_total_heal}")

            boss_abilities = []
            if m_total_attack > 0: boss_abilities.append(f"Attack {m_total_attack}")
            if m_total_shield > 0: boss_abilities.append(f"Shield {m_total_shield}")
            if m_total_heal > 0: boss_abilities.append(f"Heal {m_total_heal}")

            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Boss Abilities: {' | '.join(boss_abilities)}\n")

            print(f"Damage to Boss: {self._fmt(dmg_to_monster_total)}")
            print(f"Damage to Player: {self._fmt(dmg_to_player_total)}")
            print(f"Player Healed: {self._fmt(p_total_heal)}")
            print(f"Boss Healed: {self._fmt(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Boss: {self.saved_m}")
            print(f"Health Status -> Player: {self._fmt(self.player.stats.current_health)} | Boss: {self._fmt(self.monster.stats.current_health)}")

            # ===== Next turn =====
            input("\nPress Enter to continue...")
            self.current_turn += 1
            os.system('clear')

            # ===== Mid-turn death check =====
            if self.player.stats.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.stats.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # ===== End-of-sequence winner =====
        if self.player.stats.current_health > self.monster.stats.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'





    def player_ability_sequence(self, elixir):
        ability_sequence = []
        available_elixir = elixir
        ability_dict = {a.name: a for a in self.player.abilities}
        
        cheapest_cost = text.cheapest_ability_cost #to be updated if needed

        while available_elixir >= cheapest_cost:
            print('Elixir: ' + str(available_elixir) + '\n')

            available_abilities = []

            for ability in self.player.abilities:
                if ability.elixir <= available_elixir:
                    available_abilities.append(ability)

            print(text.combat_sequence_prompt)
            for i, ability in enumerate(available_abilities):
                print(f"{i + 1}. {ability.name}")

            choice = input(text.input_prompt).strip().lower()

            if choice.isdigit():
                choice = int(choice)
                if 0 < choice <= len(available_abilities):
                    choice = available_abilities[choice - 1].name.strip().lower()
            if choice in [a.name for a in available_abilities]:
                ability = Ability(ability_dict[choice].name)
                magnitude = 100 # placeholder
                while magnitude > available_elixir:

                    magnitude = input(text.magnitude_prompt)
                    if not magnitude.isdigit():
                        print(text.input_error_prompt)
                        magnitude = 100
                    elif magnitude.isdigit():
                        magnitude = int(magnitude)
                        if magnitude > available_elixir:
                            print(text.input_error_prompt)
                if choice == "attack":
                    ability.attack = magnitude
                    ability.magnitude = magnitude
                elif choice == "shield":
                    ability.shield = magnitude
                    ability.magnitude = magnitude
                elif choice == "heal":
                    ability.heal = magnitude
                    ability.magnitude = magnitude
                elif choice == "save":
                    ability.saved_elixir = magnitude
                    ability.magnitude = magnitude
                ability_sequence.append(ability)
                available_elixir -= magnitude
            else:
                print(text.ability_addition_error)
        return ability_sequence
    def monster_ability_sequence(self, elixir):
        ability_sequence = []
        available_elixir = elixir

        cheapest_cost = text.cheapest_ability_cost # to be updated if needed
        


        while available_elixir >= cheapest_cost:
            #random.shuffle(self.monster.abilities)
            original = random.choices(self.monster.abilities, text.monster_ability_weights)[0]
            a = Ability(original.name)
            if a.elixir <= available_elixir:
                magnitude = random.randint(1, available_elixir)
                if a.name == "attack":
                    a.attack = magnitude
                    a.magnitude = magnitude
                elif a.name == "shield":
                    a.shield = magnitude
                    a.magnitude = magnitude
                elif a.name == "heal":
                    a.heal = magnitude
                    a.magnitude = magnitude
                elif a.name == "save":
                    a.saved_elixir = magnitude
                    a.magnitude = magnitude
                available_elixir -= magnitude
                ability_sequence.append(a)
        return ability_sequence

    def returnMonsterDrop(self):
        return self.monster.drop

    def end_sequence(self):
        if self.player.stats.current_health == 0:
            print(text.defeat_text)
            return 'defeat'
        elif self.monster.stats.current_health == 0:
            print(text.victory_text)
            return 'victory'
        input('Press enter to continue...')
#Objects