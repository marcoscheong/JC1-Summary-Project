import random

import json

#Global Variables
room_types = ['treasure', 'monster']

class Game:
    """
    Class constructor for Game
    """
    def _init_(self, intro, outro, maze):
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
        """
        self.rooms = rooms
        self.starting_room = starting_room

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

#Create Room 

class Room:
    """
    Class construtor for Room
    For each room in the str_chain, it:

    Prints the room's .connects attribute (presumably a dictionary or list of connected rooms by direction)

    Then prints out the IDs of connected rooms, assuming each room has an id attribute.
    """
    def __init__(self, id: int, type: str):
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