import json

#Global Variables
room_types = ['treasure', 'battle']

class Game:
    """
    Class constructor for Game
    """
    def __init__(self, intro, outro, maze):
        pass


class Storage:
    def __init(self):
        pass
        
    def get_data(file: str)-> None:
        with open('data.json', 'r', encoding='utf-8') as f:
            # data from data.json is deserialised into data_dict
            data_dict = json.load(f)
        
    def save_data(file: str)-> None:
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
        Initializes str_chain, which will hold a chain of selected rooms for the maze.
        """
        self.rooms = rooms
        self.starting_room = starting_room
        self.str_chain = []

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

#Create Player

class Player:
    """
    Class constructor for Player instance
    """
    def __init__(self, health: int, attack: int):
        self.health = health
        self.attack = attack

    def from_storage(cls, storage: Storage, file: str):
        data = storage.get_data(file)
        return cls(health=data["Player_health"], attack=data["Player_attack"])

    def save_to_storage(self, storage: Storage, file: str):
        storage.save_data(file, {
            "Player_health": self.health,
            "Player_attack": self.attack
        })

#Create Room 

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


class Character:
    pass


list_of_rooms = []
for i in range(10):
    room =  Room(i)
    list_of_rooms.append(room)
maze = Maze(list_of_rooms, list_of_rooms[0])
maze.generate_maze()
maze.draw_rooms()
#Objects