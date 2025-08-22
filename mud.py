import random
import json
import text

class Game:
    """
    Class constructor for Game
    """
    def _init_(self, intro, outro, maze):
        self.game_state = ''
        self.maze = maze
 
    def get_options(self):
        choices = maze.room_options()
        if type(maze.current_room) == MonsterRoom:
            choices.append('fight monster')
            return choices
        elif type(maze.current_room) == TreasureRoom:
            choices.append('open chest')
            return choices
        elif type(maze.current_room) == Room:
            return choices
        
    def prompt_player_choice(self, choices):
        for i, opt in enumerate(choices):
            print(f'{(i + 1)}. {opt}')
        _input = input(text.input_prompt)
        return _input

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
        
                    
    
    def draw_rooms(self):
        """
        Method to print out each room and its connections in a clear format.
        """
        for room in self.rooms:
            if room.id % 3 == 1:  # middle column rooms
                # print(f'Room {room.id} connections:')
                has_connection = False
                for direction in text.directions:
                    connected_room = room.connects.get(direction)
                    temp = ''
                    if connected_room:
                        print(f'{direction} = Room {connected_room.id}')
                        has_connection = True
                if not has_connection:
                    print('No connections')
            if room.connects['up'] and room.connects['down'] and room.connects['left'] and room.connects['right']:
                pass
                #insert four connection here
            if room.connects['up'] and room.connects['down'] and not(room.connects['left']) and not(room.connects['right']):
                pass
                #insert two room connection vertically here
            if not(room.connects['up']) and not(room.connects['down']) and room.connects['left'] and room.connects['right']:
                pass
                #insert two room connection horizontally here
            if room.connects['up'] and room.connects['down'] and room.connects['left'] and not(room.connects['right']):
                pass
                #insert three left connection here
            if room.connects['up'] and room.connects['down'] and not(room.connects['left']) and room.connects['right']:
                pass
                #insert three right connection here
            if room.connects['up'] and not(room.connects['down']) and room.connects['left'] and room.connects['right']:
                pass
                #insert three up connection here
            if not(room.connects['up']) and room.connects['down'] and room.connects['left'] and room.connects['right']:
                pass
                #insert three down connection here
            if not(room.connects['up']) and not(room.connects['down']) and not(room.connects['left']) and room.connects['right']:
                pass
                #insert single right connection here
            if room.connects['up'] and not(room.connects['down']) and not(room.connects['left']) and not(room.connects['right']):
                pass
                #insert single up connection here
            if not(room.connects['up']) and room.connects['down'] and not(room.connects['left']) and not(room.connects['right']):
                pass
                #insert single down connection here
            if not(room.connects['up']) and not(room.connects['down']) and room.connects['left'] and not(room.connects['right']):
                pass
                #insert single left connection here


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
    def __init__(self, currency):
        self.currency = currency

    def generateItems(self):
        """
        Returns the items that are contained in the treasure room.
        Temporary function until better system is found.
        """

class MonsterRoom(Room):
    def __init__(self, availableMonsters: list):
        self.monster = ''
        self.availableMonsters = availableMonsters

    def generateMonster(self):
        """
        Returns the randomly generated monster in the room.
        Temporary function until better system is found.
        """
        if len(self.availableMonsters) == 0:
            return 'list of monsters is empty'
        i = random.randint(len(self.availableMonsters) - 1)
        return self.availableMonsters[i]


# CHARACTER CLASSES
class Character:
    def __init__(self, stats):
        self.stats = stats
        # self.inventory = Inventory() (to be updated)

class Player:
    def __init__(self, health: int = 0, attack: int = 0):
        self.health = health
        self.attack = attack

    def load_from_storage(self, storage: Storage, file: str):
        data = storage.get_data(file)
        self.health = data["Player_health"]
        self.attack = data["Player_attack"]

    def save_to_storage(self, storage: Storage, file: str):
        storage.save_data(file, {
            "Player_health": self.health,
            "Player_attack": self.attack
        })
    def inventory(self):
        pass



class Monster(Character):
    def __init__(self, stats):
        self.stats = stats

class Stats():
    def __init__(self, maxHealth: int, attack: int):
        self.maxHealth = maxHealth
        self.attack = attack
        self.currentHealth = maxHealth
    
    def takeDamage(self, damage):
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
        self.saved_elixir = 0

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

            player_seq = player_ability_sequence(p_elixir)
            monster_seq = monster_abilty_sequence(m_elixir)

            if len(player_seq) > len(monster_seq):
                for i in range(len(monster_seq)):
                    p_dmg_taken = monster_seq[i].attack - player_seq[i].shield
                    m_dmg_taken = player_seq[i].attack - monster_seq[i].shield

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
                
                for i in range(len(monster_seq), len(player_seq)):
                    m_dmg_taken = player_seq[i].attack

                    p_healed = player_seq[i].heal

                    self.saved_p = player_seq[i].saved_elixir
            elif len(player_seq) < len(monster_seq):
                for i in range(len(player_seq)):
                    p_dmg_taken = monster_seq[i].attack - player_seq[i].shield
                    m_dmg_taken = player_seq[i].attack - monster_seq[i].shield

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
                
                for i in range(len(player_seq), len(monster_seq)):
                    p_dmg_taken = monster_seq[i].attack

                    m_healed = monster_seq[i].heal

                    self.saved_m = monster_seq[i].saved_elixir
            else: 
                for i in range(len(player_seq)):
                    p_dmg_taken = monster_seq[i].attack - player_seq[i].shield
                    m_dmg_taken = player_seq[i].attack - monster_seq[i].shield

                    p_healed = player_seq[i].heal
                    m_healed = monster_seq[i].heal

                    self.saved_p = player_seq[i].saved_elixir
                    self.saved_m = monster_seq[i].saved_elixir
            current_turn += 1
        self.end_sequence()
    def player_ability_sequence(self, elixir):
        ability_sequence = []
        available_elixir = elixir
        ability_dict = {a.name: a for a in abilities}
        
        cheapest_cost = text.cheapest_ability_cost #to be updated if needed

        while elixir > cheapest_cost:
            available_abilities = []

            for ability in self.player.abilities():
                if ability.elixir > available_elixir:
                    available_abilities.append(ability)

            print(text.combat_sequence_prompt)
            for i, ability in enumerate(available_abilities):
                print(f"{i}. {ability.name}")

            choice = input(text.input_prompt).strip().lower()

            if choice in [a.name for a in available_abilites]:
                ability = ability_dict[choice]
                magnitude = 100 # placeholder
                while magnitude > available_elixir:
                    magnitude = input(text.magnitude_prompt)
                    if magnitude > available_elixir:
                        print(text.input_error_prompt)
                if choice == "attack":
                    ability.attack = magnitude
                elif choice == "shield":
                    ability.shield = magnitude
                elif choice == "heal":
                    ability.heal = magnitude
                elif choice == "save":
                    ability.saved_elixir = magnitude
                ability_sequence.append(ability)
            else:
                print(text.ability_addition_error)
        return ability_sequence
    def monster_abilty_sequence(self, elixir):
        ability_sequence = []
        available_elixir = elixir
        random.shuffle(self.monster.abilities())
        
        cheapest_cost = text.cheapest_ability_cost # to be updated if needed
        
        while available_elixir > cheapest_cost:
            for ability in self.monster.abilities():
                if ability.elixir < available_elixir:
                    ability_sequence.append(move)
        return ability_sequence

    def end_sequence(self):
        #return victory/defeat result
        pass

list_of_rooms = []
for i in range(10):
    room =  Room(i)
    list_of_rooms.append(room)
maze = Maze(list_of_rooms, list_of_rooms[0])
maze.generate_maze()
maze.draw_rooms()
#Objects