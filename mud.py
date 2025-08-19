import random
import json

#Global Variables
room_types = ['treasure', 'monster']

class Game:
    """
    Class constructor for Game
    """
    def _init_(self, intro, outro, maze):
        self.game_state = ''
        self.maze = maze
 
    def get_options(self):
        if game_state == 'travelling':
            return maze.room_options()
        elif game_state == 'fighting':
            #todo
            pass
        
    def get_actions(self, choices, choice):
        chosen = choices[choice - 1]
        if chosen.topic == 'travel':
            maze.travel_to(chosen)

    def execute(self, action):
        pass

class Storage:
    def __init(self):
        pass
        
    def get_data(file: str)-> None:
        with open('data.json', 'r', encoding='utf-8') as f:
            # data from data.json is deserialised into data_dict
            data_dict = json.load(f)
            
    def save_data(self, file: str)-> None:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(obj, f)

#List of things we need to do
#Create maze
class Maze:
    """
    Class constructor for Maze
    """
    def __init__(self, rooms: dict['Room'], starting_room):
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
                down_room.connection(room, 'top')
                    
    
    def draw_rooms(self):
        """
        Method to print out each room and its connections in a clear format.
        """
        for room in self.rooms:
            if room.id % 3 == 1:  # middle column rooms
                print(f'Room {room.id} connections:')
                has_connection = False
                for direction in ['left', 'right', 'top', 'down']:
                    connected_room = room.connects.get(direction)
                    if connected_room:
                        print(f'{direction} = Room {connected_room.id}')
                        has_connection = True
                if not has_connection:
                    print('  No connections')

    def room_options(self):
        options = []
        for direction in ['top', 'down', 'left', 'right']:
            connected_room = current_room.connects.get(direction)
            if connected_room:
                options.append(direction)
        return options

    def travel_to(self, direction):
        if current_room[direction]:
            current_room = current_room[direction]
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
        self.connects = {'top': None, 'left': None, 'right': None, 'down': None}

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

class Monster(Character):
    def __init__(self, stats):
        pass

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

class CombatSequence():
    def __init__(self, character, monster, points: int):
        self.points = points

    def startSequence(self):
        #input logic for combat sequence
        pass
    
    def endSequence(self):
        #return victory/defeat result
        pass

class Choice():
    def __init__(self, topic, details):
        self.topic = topic
        self.details = details

list_of_rooms = []
for i in range(10):
    room =  Room(i)
    list_of_rooms.append(room)
maze = Maze(list_of_rooms, list_of_rooms[0])
maze.generate_maze()
maze.draw_rooms()
#Objects