# Game module - Game controller and main loop (UI + game logic combined)
import os
import select
import sys
import tempfile
import time
from campusmud import text
from campusmud.storage import Storage
from campusmud.models import Stats
from campusmud.entities import Player, Monster
from campusmud.maze import Room, TreasureRoom, MonsterRoom, BossRoom, Maze
from campusmud.combat import CombatSequence
from campusmud.text import prompt_player_choice


class Game:
    """
    Main game controller with state management.
    """
    def __init__(self):
        self.game_state = ''
        self.maze = None
        self.storage = Storage()
        self.player = None

    def set_state(self, state):
        """
        Set the current game state.
        """
        self.game_state = state
    
    def get_state(self):
        """
        Get the current game state.
        """
        return self.game_state
    
    def get_maze(self):
        """
        Get the maze object.
        """
        return self.maze
 
    def get_options(self):
        """
        Get available options based on current game state and room type.
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
        
    def start_game(self):
        """
        Start a new game with a fresh maze and player.
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
        Load a saved game from file.
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

    def pretty_print(self, text_content):
        """
        Print text character-by-character for aesthetics.
        """
        i = 0
        while i < len(text_content):
            try:
                if select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline()
                    sys.stdout.write(text_content[i:]) 
                    break
            except:
                # Fallback for non-tty/Windows environments
                sys.stdout.write(text_content[i:])
                break
            sys.stdout.write(text_content[i])
            sys.stdout.flush()
            time.sleep(0.032)
            i += 1

    def quit_game(self):
        """
        Exit the game.
        """
        sys.exit()

    def welcome(self):
        """
        Display welcome menu when user first starts the program.
        """
        print(text.welcome_prompt)
        choices = self.get_options()
        chosen = False
        while chosen == False:
            choice = prompt_player_choice(choices)
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
        Initialize a new player.
        """
        stats = Stats(text.default_health, text.default_attack)
        self.player = Player(stats)
        self.player.create_new_storage(self.storage, text.player_save_file)
    
    def load_player(self):
        """
        Load player from saved file.
        """
        atk = self.storage.get_data(text.player_save_file).get("Player_attack", text.default_attack)
        current_health = self.storage.get_data(text.player_save_file).get("Player_current_health", text.default_health)
        max_health = self.storage.get_data(text.player_save_file).get("Player_max_health", text.default_health)
        stats = Stats(max_health, atk)
        self.player = Player(stats)
        self.player.load_from_storage(self.storage, text.player_save_file)

    def get_player(self):
        """
        Get the player object.
        """
        return self.player

    def load_data(self):
        """
        Loader method for data.
        """
        pass

    def save_all_data(self, file): 
        """
        Save all current game variables to file.
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

    def display_room_info(self):
        """
        Display information about the current room based on its type.
        """
        current_room = self.maze.current_room
        if isinstance(current_room, TreasureRoom):
            print(text.treasure_room_text if not current_room.claimed else text.claimed_treasure_room_text)
        elif isinstance(current_room, MonsterRoom):
            print(text.monster_room_text if not current_room.claimed else text.claimed_monster_room_text)
        elif isinstance(current_room, BossRoom):
            if not current_room.claimed:
                command = prompt_player_choice(
                    preamble=f"You have encountered the boss: {text.boss_monster}. Do you want to fight this boss?",
                    choices=self.get_options()
                )
                if command in ['quit', 'exit']:
                    self.save_all_data(text.player_save_file)
                    print(text.thanks_message)
                    sys.exit()
                elif command in ['go back', 'back']:
                    self.set_state('travel')
                elif command in ['fight boss', 'fight', 'challenge the boss', 'challenge boss']:
                    os.system('clear')
                    monster = current_room.boss_monster
                    input(f"You have encountered {text.boss_monster}.\n Atk: {monster.stats.attack}, HP: {monster.stats.max_health}\nPress enter to continue...")
                    os.system('clear')
                    combat_seq = CombatSequence(self.get_player(), monster, 3, 20)
                    result = combat_seq.start_boss_sequence()
                    if result == 'victory':
                        current_room.claimed = True
                        self.save_all_data(text.player_save_file)
                        print('You have defeated the boss! Congratulations on completing the game!')
                        input('Press enter to exit.')
                        sys.exit()
                    elif result == 'defeat':
                        command = prompt_player_choice(
                            preamble="You have been defeated by the boss. Game over.",
                            choices=['Retry', 'Quit']
                        )
                        if command in ['quit', 'exit']:
                            default_data = self.storage.get_data(text.default_save_file)
                            self.storage.save_data(text.player_save_file, default_data)
                            print(text.thanks_message)
                            sys.exit()
                        elif command in ['retry', 'start', 'play']:
                            self.__init__()
                            self.set_state('start')
                            self.welcome()
        else:
            print("You have defeated the boss. Do you want to travel to another room?")

    def use_item(self, item_name):
        """
        Handle the logic for using an item.
        """
        if item_name == 'health potion':
            magnitude = self.get_player().stats.max_health * 0.2
            self.get_player().health_potion(magnitude)
            self.get_player().recalculate_stats()
            print('\n' + text.equip_spacing_text)
            print(f"Your max health has increased by {magnitude}!")
            print(text.equip_spacing_text + '\n')
        elif item_name == 'healing potion':
            magnitude = self.get_player().stats.max_health * 0.2
            self.get_player().stats.heal(magnitude)
            print('\n' + text.equip_spacing_text)
            print(f'You have healed {magnitude} health!')
            print(text.equip_spacing_text + '\n')
        elif item_name == 'attack potion':
            magnitude = self.get_player().stats.attack * 0.2
            self.get_player().atk_potion(magnitude)
            self.get_player().recalculate_stats()
            print('\n' + text.equip_spacing_text)
            print(f'Your attack has increased by {magnitude}!')
            print(text.equip_spacing_text + '\n')
        input("\nPress enter to continue...")

def run():
    """
    Main game loop - handles user input and game state.
    """
    game = Game()
    game.set_state('start')
    game.welcome()

    while True:
        os.system('clear')

        if game.game_state == 'travel':
            game.maze.draw_rooms()

        # Display room-specific text
        game.display_room_info()
        
        # Main command processing
        command = prompt_player_choice(
            preamble="What would you like to do?",
            choices=game.get_options()
        )
        if command in ['quit', 'exit']:
            game.save_all_data(text.player_save_file)
            print(text.thanks_message)
            sys.exit()        
        elif command == 'enter boss chamber' or command.startswith('enter boss'):
            game.get_maze().travel_to('boss chamber')
            game.get_maze().draw_rooms()        
        elif command in ['view inventory', 'inventory', 'inv']:
            game.set_state('inventory')
            while game.get_state() == 'inventory':
                os.system('clear')
                print(game.get_player().inventory.return_inventory())
                choices = game.get_options()
                command = prompt_player_choice(
                    preamble=game.get_player().stats.return_stats(),
                    choices=game.get_options()
                )
                if command in ['go back', 'back']:
                    game.set_state('travel')
                elif command in ['use item']:
                    item_name = input('Please enter the name of the item you want to use: ').strip().lower()

                    if item_name.isdigit():
                        print(text.input_error_prompt)
                        input("\nPress enter to continue...")

                    elif item_name not in text.Consumable:
                        print(text.input_error_prompt)
                        input("\nPress enter to continue...")

                    elif game.get_player().inventory.use_item(item_name):
                        game.use_item(item_name)
                        game.set_state('travel')

                    else:
                        print(text.input_error_prompt)
                        input("\nPress enter to continue...")

        elif command.startswith('go'):
            direction = command.split()[1]
            if direction in text.directions:
                game.maze.travel_to(direction)
                game.save_all_data(text.player_save_file)
            else:
                print(text.input_error_prompt)
        
        elif command.startswith('open'):
            if type(game.get_maze().current_room) == TreasureRoom:
                # Open chest logic
                treasure_type = game.get_maze().current_room.get_type()
                drop = game.get_maze().current_room.get_drops()
                if treasure_type == 'weapon' or treasure_type == 'armour':
                    game.set_state('item chest')
                    print('\n' + text.equip_spacing_text)
                    if treasure_type == 'weapon':
                        print(f"You have found a {drop} (atk: {text.Weapon[drop]})!")
                    elif treasure_type == 'armour':
                        slot = text.ArmourSlots[drop]
                        print(f"You have found {drop} (slot: {slot}, def: {text.Armour[drop]})!")
                    print(text.equip_spacing_text + '\n')

                    command = prompt_player_choice(
                        preamble=text.equip_spacing_text,
                        choices=game.get_options()
                    )
                    if command in ['go back', 'back']:
                        game.set_state('travel')
                    elif command in ['equip item', 'equip']:
                        if treasure_type == 'weapon':
                            game.get_player().inventory.equip_weapon(drop)
                            game.get_player().recalculate_stats()
                            input('\nPress enter to continue...')
                        elif treasure_type == 'armour':
                            slot = text.ArmourSlots[drop]
                            game.get_player().inventory.equip_armour(slot, drop)
                            game.get_player().recalculate_stats()
                            input('\nPress enter to continue...')

                        game.get_maze().current_room.drop = None
                        game.get_maze().current_room.claimed = True
                        game.set_state('travel')
                elif treasure_type == 'consumable':
                    game.get_player().inventory.add_item(drop)
                    print('\n' + text.equip_spacing_text)
                    print('You have obtained a ' + drop + '!')
                    game.set_state('consumable chest')
                    command = prompt_player_choice(
                        preamble=text.equip_spacing_text,
                        choices=game.get_options()
                    )
                    if command in ['go back', 'back']:
                        game.set_state('travel')
                    elif command in ['consume item', 'consume']:
                        if drop in text.Consumable:
                            if game.get_player().inventory.use_item(drop):
                                game.use_item(drop)
                            else:
                                print(text.input_error_prompt)
                        else:
                            print(text.input_error_prompt)
                    game.get_maze().current_room.drop = None
                    game.get_maze().current_room.claimed = True
                    game.set_state('travel')
            
        elif command.startswith('fight'):
            os.system('clear')
            monster = Monster(Stats(text.Monsters[game.maze.current_room.monster][0], text.Monsters[game.maze.current_room.monster][1]))
            input(f"You have encountered a {game.maze.current_room.monster}.\n Atk: {monster.stats.attack}, HP: {monster.stats.max_health}\nPress enter to continue...")
            os.system('clear')
            combat_seq = CombatSequence(game.get_player(), monster, 3, 20)
            result = combat_seq.start_sequence()
            if result == 'victory':
                current_room = game.maze.current_room
                current_room.monster = None
                current_room.claimed = True

                drop = current_room.drop
                if drop.type == 'weapon':
                    print(f"You have obtained a {drop.drop}({text.Weapon[drop.drop]})!")
                elif drop.type == 'armour':
                    slot = text.ArmourSlots[drop.drop]
                    print(f"You have obtained {drop.drop} (slot: {slot}, def: {text.Armour[drop.drop]})!")
                game.set_state('item chest')
                command = prompt_player_choice(
                    preamble="What would you like to do?",
                    choices=game.get_options()
                )
                if command in ['go back', 'back']:
                    game.set_state('travel')
                elif command in ['equip item', 'equip']:
                    if drop.drop in text.Weapon:
                        game.get_player().inventory.equip_weapon(drop.drop)
                        game.get_player().recalculate_stats()
                        game.save_all_data(text.player_save_file)
                        input('\nPress enter to continue...')
                    elif drop.drop in text.Armour:
                        slot = text.ArmourSlots[drop.drop]
                        game.get_player().inventory.equip_armour(slot, drop.drop)
                        game.get_player().recalculate_stats()
                        game.save_all_data(text.player_save_file)
                        input('\nPress enter to continue...')
                    game.set_state('travel')

                game.set_state('travel')
                game.get_player().recalculate_stats()
                game.save_all_data(text.player_save_file)
            elif result == 'defeat':
                command = prompt_player_choice(
                    preamble=(
                        "You have been defeated by the monster. Game over.\n"
                        "Do you want to retry?"
                    ),
                    choices=['Retry', 'Quit']
                )
                if command in ['quit', 'exit']:
                    default_data = game.storage.get_data(text.default_save_file)
                    game.storage.save_data(text.player_save_file, default_data)
                    print(text.thanks_message)
                    sys.exit()
                elif command in ['retry', 'start', 'play']:
                    game = Game()
                    game.set_state('start')
                    game.welcome()
        else:
            print(text.input_error_prompt)
