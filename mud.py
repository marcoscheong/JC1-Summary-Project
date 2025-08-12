import json

#Global Variables
room_types = ['treasure', 'battle']

class Game:
    """
    Class constructor for Game
    """
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
    def __init__(self, rooms: list['Room'], starting_room):
        self.rooms = rooms
        self.starting_room = starting_room
        self.str_chain = []

    def generate_maze(self):
        """
        Function to generate the layout of rooms
        """
        #list of straight chain rooms
        for i, room in enumerate(self.rooms):
            if i % 2 == 0:
                self.str_chain.append(room)
        for i, room in enumerate(self.str_chain):
            if i != len(self.str_chain) - 1:
                room.connection(self.str_chain[i + 1], 'top')
            if i != 0:
                room.connection(self.str_chain[i - 1], 'down')
        
    
    def draw_rooms(self):
        """
        Method to print out the room in the format of a mini map
        """
        for i, room in enumerate(self.str_chain):
            print(room.connects)
            for dir in room.connects:
                if dir != None:
                    print(f'{self.str_chain[i].id}, connections: {dir.id}')

#Create Room

class Room:
    """
    Class construtor for Room
    """
    def __init__(self, id: int):
        self.id = id
        #self.type = type
        self.top, self.left, self.right, self.down = None, None, None, None
        self.connects = [self.top, self.left, self.right, self.down]

    def connection(self, room, direction):
        """
        Connects self to room
        """
        if direction == 'top':
            self.top = room
        if direction == 'right':
            self.right = room
        if direction == 'left':
            self.left = room
        if direction == 'down':
            self.down = room
        
        self.connects = [self.top, self.left, self.right, self.down]


class Character:
    pass


list_of_rooms = []
for i in range(5):
    room =  Room(i)
    list_of_rooms.append(room)
maze = Maze(list_of_rooms, list_of_rooms[0])
maze.generate_maze()
maze.draw_rooms()
#Objects



