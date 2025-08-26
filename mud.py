import time
import random
import json
import text
import sys
import select

class Game:
    """
    Class constructor for Game
    """
    def _init_(self, storage):
        self.game_state = ''
        self.maze = None
        self.storage = storage
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
                choices.insert(0, 'Fight monster')
                return choices
            elif type(self.maze.current_room) == TreasureRoom:
                choices.insert(0, 'Open chest')
                return choices
            elif type(self.maze.current_room) == Room:
                return choices
        
    def prompt_player_choice(self, choices):
        for i, opt in enumerate(choices):
            print(f'{(i + 1)}. {opt}')
            time.sleep(0.05)
        _input = input(text.input_prompt)
        return _input

    def start_game(self):
        #instantiate maze
        rooms = []
        rooms.append(Room(0))
        for i in range(1, text.maze_size):
            if i % 2 == 0:
                room = MonsterRoom((i + 1), text.Monsters.keys())
                room.generateMonster()
                rooms.append(room)
            elif i % 2 == 1:
                rooms.append(TreasureRoom(i + 1))
            else:
                rooms.append(Room(i + 1))
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
    
    def get_player(self):
        return self.player

    def load_data(self):
        pass

    def store_currentdata(self, file):    
        self.storage.save_data(file, {
            "Room_id": self.maze.current_room.id
        })
        

class Storage:
    def __init(self):
        pass
        
    def get_data(self)-> None:
        with open('data.json', 'r', encoding='utf-8') as f:
            # data from data.json is deserialised into data_dict
            data_dict = json.load(f)
            return data_dict
            #f.close()
            
    def save_data(self, obj)-> None:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(obj, f)
            #f.close()

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
        """
        Function to generate the layout of rooms in a 3-column grid.
        """
        num_cols = 3
        num_rows = len(self.rooms) // num_cols

        for i, room in enumerate(self.rooms):
            row = i // num_cols # gives row no
            col = i % num_cols # gives col no

            # Connect right 
            if col < num_cols - 1 and (i + 1) < len(self.rooms):
                right_room = self.rooms[i + 1]
                room.connection(right_room, 'right')
                right_room.connection(room, 'left')

            # Connect down 
            if row < num_rows - 1 and (i + num_cols) < len(self.rooms):
                down_room = self.rooms[i + num_cols]
                room.connection(down_room, 'down')
                down_room.connection(room, 'up')
        
    def get_room_key(self, room):
        up, down, left, right = (
            room.connects['up'], 
            room.connects['down'], 
            room.connects['left'], 
            room.connects['right']
        )

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
        return "NONE"
    
    def draw_rooms(self):
        """
        Method to print out each room and its connections in a clear format as a proper grid.
        """
        row_chunks = []
        rooms_per_row = 3

        # Build the grid row by row
        for row_start in range(0, len(self.rooms), rooms_per_row):
            row_rooms = self.rooms[row_start:row_start + rooms_per_row]

            # Collect arts for this row
            row_arts = []
            for room in row_rooms:
                if room.id == self.current_room.id:
                    row_arts.append(text.player_rooms[self.get_room_key(room)])
                else:
                    row_arts.append(text.rooms[self.get_room_key(room)])

            # Determine max height for this row
            max_height = max(len(r.strip("\n").splitlines()) for r in row_arts)
            max_width = max(max(len(line) for line in r.strip("\n").splitlines()) for r in row_arts)

            # Initialize row chunk
            row_chunk = [[] for _ in range(max_height)]

            # Pad rooms and add to row_chunk
            for art in row_arts:
                lines = art.strip("\n").splitlines()
                lines = [line.ljust(max_width) for line in lines]

                # Pad bottom if shorter than row's max_height
                while len(lines) < max_height:
                    lines.append(" " * max_width)

                for i, line in enumerate(lines):
                    row_chunk[i].append(line)

            row_chunks.append(row_chunk)

        # Build final string
        map_str = ""
        for row in row_chunks:
            for line in row:
                map_str += "".join(line) + "\n"

        print(map_str)


    def room_options(self):
        options = []
        for direction in text.directions:
            connected_room = self.current_room.connects.get(direction)
            if connected_room:
                options.append('go ' + direction)
        return options

    def travel_to(self, direction):
        connected_room = self.current_room.connects.get(direction)
        if connected_room:
            self.current_room = connected_room
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
    def __init__(self, id):
        super().__init__(id)

    def generateItems(self):
        """
        Returns the items that are contained in the treasure room.
        Temporary function until better system is found.
        """

class MonsterRoom(Room):
    def __init__(self, id: int, availableMonsters: list):
        super().__init__(id)
        self.monster = ''
        self.availableMonsters = availableMonsters

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

    def load_from_storage(self, storage: Storage, file: str):
        data = storage.get_data(file)
        self.stats.maxHealth = data["Player_max_health"]
        self.stats.currentHealth = data["Player_current_health"]
        self.stats.attack = data["Player_attack"]
        self.inventory = Inventory(storage, file)

    def save_to_storage(self, storage: Storage, file: str):
        storage.save_data(file, {
            "Player_health": self.stats.maxHealth,
            "Player_current_health": self.stats.currentHealth,
            "Player_attack": self.stats.attack
        })
        self.inventory.save_inventory()

class Inventory:
    def __init__(self, storage: Storage, file: str):
        self.storage = storage
        self.file = file
        try:
            data = self.storage.get_data(file)
            self.items = data.get("items", {})
        except FileNotFoundError:
            self.items = {}
            self.save_inventory()  # create file if not exists

    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item and save to JSON."""
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity
        self.save_inventory()

    def use_item(self, item_name: str, quantity: int = 1):
        """Use an item and save to JSON."""
        if item_name not in self.items:
            print(f"{item_name} not found in inventory.")
            return False
        if self.items[item_name] < quantity:
            print(f"Not enough {item_name} to use.")
            return False
        
        self.items[item_name] -= quantity
        if self.items[item_name] <= 0:
            del self.items[item_name]
        self.save_inventory()
        return True

    def remove_item(self, item_name: str):
        """Remove an item completely."""
        if item_name in self.items:
            del self.items[item_name]
            self.save_inventory()
        else:
            print(f"{item_name} not found in inventory.")

    def save_inventory(self):
        """Save current inventory to the JSON file."""
        self.storage.save_data(self.file, {"items": self.items})

    def show_inventory(self):
        """Print the current inventory."""
        if not self.items:
            print("Inventory is empty.")
        else:
            print("Current Inventory:")
            for item, qty in self.items.items():
                print(f"{item}: {qty}")
    

class Monster(Character):
    def __init__(self, stats):
        super().__init__(stats)

class Drop():
    def __init__(self, weaponWeights, armourWeights):
        self.weaponWeights = weaponWeights
        self.armourWeights = armourWeights
    
    def generateDrop(self):
        random = random.randint(0, 1)
        if random == 0:
            drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
        elif random == 1:
            drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
        return drop

class Stats():
    def __init__(self, maxHealth: int, attack: int):
        self.maxHealth = maxHealth
        self.attack = attack
        self.currentHealth = maxHealth
    
    def take_damage(self, damage):
        if (self.currentHealth - damage) <= 0:
            return 'died'
        else:
            self.currentHealth -= damage
    
    def heal(self, healAmount):
        if (self.currentHealth + healAmount) > self.maxHealth:
            self.currentHealth = self.maxHealth
        else:
            self.currentHealth += healAmount

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
    def start_sequence(self):
        #input logic for combat sequence
        while self.current_turn < self.max_turns:
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m

            self.saved_p = 0
            self.saved_m = 0

            print(text.combat_spacing_text)

            print(f'Current player health: {self.player.stats.currentHealth}')
            print(f'Current monster health: {self.monster.stats.currentHealth}\n')

            player_seq = self.player_ability_sequence(p_elixir)
            monster_seq = self.monster_ability_sequence(m_elixir)

            player_str = '\nP: '
            for i in range(len(player_seq)):
                player_str += f'{player_seq[i].name}({player_seq[i].magnitude}) '
            print(player_str)
            monster_str = 'M: '
            for i in range(len(monster_seq)):
                monster_str += f'{monster_seq[i].name}({monster_seq[i].magnitude}) '
            print(monster_str + '\n')
            if len(player_seq) > len(monster_seq):
                for i in range(len(monster_seq)):
                    p_dmg_taken = (monster_seq[i].attack - player_seq[i].shield) * (self.monster.stats.attack / 10)
                    m_dmg_taken = (player_seq[i].attack - monster_seq[i].shield) * (self.player.stats.attack  / 10)

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    if p_dmg_taken < 0:
                        p_dmg_taken = 0
                    if m_dmg_taken < 0:
                        m_dmg_taken = 0
                    p_state = self.player.stats.take_damage(p_dmg_taken)
                    m_state = self.monster.stats.take_damage(m_dmg_taken)
                    self.player.stats.heal(p_healed)
                    self.monster.stats.heal(m_healed)
                    print(f'Player has taken {p_dmg_taken} and healed {p_healed}')
                    time.sleep(0.5)
                    print(text.ability_spacing_text)
                    time.sleep(0.5)
                    print(f'Monster has taken {m_dmg_taken} and healed {m_healed}')
                    if p_state == 'died':
                        return self.end_sequence()
                    if m_state == 'died':
                        return self.end_sequence()

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
                
                for i in range(len(monster_seq), len(player_seq)):
                    m_dmg_taken = player_seq[i].attack * self.player.stats.attack / 10 

                    p_healed = player_seq[i].heal
                    
                    time.sleep(0.5)
                    print(text.ability_spacing_text)
                    time.sleep(0.5)
                    
                    if p_healed != 0:
                        print(f'Played has healed {p_healed}')
                    if m_dmg_taken != 0:
                        print(f'Monster has taken {m_dmg_taken}')

                    self.monster.stats.take_damage(m_dmg_taken)
                    self.player.stats.heal(p_healed)

                    self.saved_p = player_seq[i].saved_elixir
            elif len(player_seq) < len(monster_seq):
                for i in range(len(player_seq)):
                    p_dmg_taken = (monster_seq[i].attack - player_seq[i].shield) * (self.monster.stats.attack / 10)
                    m_dmg_taken = (player_seq[i].attack - monster_seq[i].shield) * (self.player.stats.attack  / 10)

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    if p_dmg_taken < 0:
                        p_dmg_taken = 0
                    if m_dmg_taken < 0:
                        m_dmg_taken = 0
                    p_state = self.player.stats.take_damage(p_dmg_taken)
                    m_state = self.monster.stats.take_damage(m_dmg_taken)
                    self.player.stats.heal(p_healed)
                    self.monster.stats.heal(m_healed)
                    print(f'Player has taken {p_dmg_taken} and healed {p_healed}')
                    time.sleep(0.5)
                    print(text.ability_spacing_text)
                    time.sleep(0.5)
                    print(f'Monster has taken {m_dmg_taken} and healed {m_healed}')
                    if p_state == 'died':
                        return self.end_sequence()
                    if m_state == 'died':
                        return self.end_sequence()

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
                
                for i in range(len(player_seq), len(monster_seq)):
                    p_dmg_taken = monster_seq[i].attack * self.monster.stats.attack / 10

                    m_healed = monster_seq[i].heal
                    time.sleep(0.5)
                    print(text.ability_spacing_text)
                    time.sleep(0.5)

                    if p_dmg_taken != 0:
                        print(f'Player has taken {p_dmg_taken}')
                    if m_healed != 0:
                        print(f'Monster has healed {m_healed}')

                    self.player.stats.take_damage(p_dmg_taken)
                    self.monster.stats.heal(m_healed)

                    self.saved_m = monster_seq[i].saved_elixir
            else: 
                for i in range(len(player_seq)):
                    p_dmg_taken = (monster_seq[i].attack - player_seq[i].shield) * (self.monster.stats.attack / 10)
                    m_dmg_taken = (player_seq[i].attack - monster_seq[i].shield) * (self.player.stats.attack  / 10)

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    if p_dmg_taken < 0:
                        p_dmg_taken = 0
                    if m_dmg_taken < 0:
                        m_dmg_taken = 0
                    p_state = self.player.stats.take_damage(p_dmg_taken)
                    m_state = self.monster.stats.take_damage(m_dmg_taken)
                    self.player.stats.heal(p_healed)
                    self.monster.stats.heal(m_healed)
                    print(f'Player has taken {p_dmg_taken} and healed {p_healed}')
                    time.sleep(0.5)
                    print(text.ability_spacing_text)
                    print(f'Monster has taken {m_dmg_taken} and healed {m_healed}')
                    time.sleep(0.5)
                    if p_state == 'died':
                        return self.end_sequence()
                    if m_state == 'died':
                        return self.end_sequence()

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
            
            print(f"========= End of turn {self.current_turn} =========")
            input()
            self.current_turn += 1
        return self.end_sequence()
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
                print(f'{a.name} with magnitude: {magnitude}')
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

    def end_sequence(self):
        #return victory/defeat result
        print('combat done') # placeholder
#Objects