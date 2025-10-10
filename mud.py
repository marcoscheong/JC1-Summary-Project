import json
import os
import random
import select
import sys
import tempfile
import text
import time
from campusmud.storage import Storage
from campusmud.models import Stats, Drop, Ability
from campusmud.entities import Character, Player, Monster, Inventory
from campusmud.maze import Room, TreasureRoom, MonsterRoom, BossRoom, Maze
from campusmud.combat import CombatSequence


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
        """
        setter method for game state 
        """
        self.game_state = state
    
    def get_state(self):
        """
        getter method for game state
        """
        return self.game_state
    
    def get_maze(self):
        """
        getter method for maze
        """
        return self.maze
 
    def get_options(self):
        """
        getter method to get options to display appropriately
        """
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
        """
        displays choices and gets input from player
        """
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
        """
        starts game sequence
        """
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

    def load_game(self):
        """
        load method for json
        """
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
        for room in rooms:
            if type(room) == TreasureRoom or type(room) == MonsterRoom or type(room) == BossRoom:
                if room.id in self.storage.get_data(text.player_save_file).get("Claimed_rooms", []):
                    room.claimed = True
        self.maze = Maze(rooms, rooms[0])
        self.maze.generate_maze()
        self.load_player()
        print()
        print(text.loaded_text)
        print(text.printing_text_large_spacing)
        input()
        self.maze.draw_rooms()
        self.set_state('travel')

    def pretty_print(self, text):
        """
        prints out text charcter-by-character; aesthetics
        """
        i = 0
        while i < len(text):
            try:
                if select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline()
                    sys.stdout.write(text[i:]) 
                    # sys.stdout.flush()
                    break
            except:
                # Fallback for non-tty/Windows environments
                sys.stdout.write(text[i:])
                break
            sys.stdout.write(text[i])
            sys.stdout.flush()
            time.sleep(0.032)
            i += 1

    def quit_game(self):
        """
        exits game system
        """
        sys.exit()

    def welcome(self):
        """
        displays menu that shows when user first starts program
        """
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
            elif choice == 'load' or choice == '2':
                chosen = True
                if os.path.exists(text.player_save_file):
                    self.load_game()
                else:
                    print(text.load_error_text)
                    self.start_game()
            elif choice == 'quit' or choice == '3':
                chosen = True
                self.quit_game()
            elif choice == 'how to play' or choice == '4':
                print(text.how_to_play_text)
                print()
                input("Press Enter to continue...")

    def create_player(self):
        """
        initialisation of player
        """
        stats = Stats(text.default_health, text.default_attack)
        self.player = Player(stats)
        self.player.create_new_storage(self.storage, text.player_save_file)
    
    def load_player(self):
        """
        load method for player
        """
        atk = self.storage.get_data(text.player_save_file).get("Player_attack", text.default_attack)
        current_health = self.storage.get_data(text.player_save_file).get("Player_current_health", text.default_health)
        max_health = self.storage.get_data(text.player_save_file).get("Player_max_health", text.default_health)
        stats = Stats(max_health, atk)
        self.player = Player(stats)
        self.player.load_from_storage(self.storage, text.player_save_file)

    def get_player(self):
        """
        getter method for player
        """
        return self.player

    def load_data(self):
        """
        loader method for data
        """
        pass

    def save_all_data(self, file): 
        """
        saves data of all current variables
        """
        claimed_rooms = []
        for room in self.maze.rooms:
            if isinstance(room, TreasureRoom) and room.claimed:
                if room.id not in self.storage.get_data(file).get("Claimed_rooms", []):
                    claimed_rooms.append(room.id)
            elif isinstance(room, MonsterRoom) and room.claimed:
                if room.id not in self.storage.get_data(file).get("Claimed_rooms", []):
                    claimed_rooms.append(room.id)
            elif isinstance(room, BossRoom) and room.claimed:
                if room.id not in self.storage.get_data(file).get("Claimed_rooms", []):
                    claimed_rooms.append(room.id)
        self.storage.save_data(file, {
            "Room_id": self.maze.current_room.id,
        })
        self.storage.save_data(file, {
            "Claimed_rooms": claimed_rooms
        })
        self.player.save_to_storage(self.storage, file)
