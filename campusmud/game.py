# Game module - Game controller and main loop (UI + game logic combined)

import random
from typing import Optional

from campusmud import config, entities, models, text
from campusmud.storage import Storage
from campusmud.maze import Room, TreasureRoom, MonsterRoom, BossRoom, Maze
from campusmud.combat import CombatSequence
from campusmud.text import prompt_player_choice

BOSS_NAME = "Origin of Chaos"


def next_multiple_of_5(n: int) -> int:
    """Return the next multiple of 5 greater than or equal to n."""
    while n % 5 != 0:
        n += 1
    return n


def generate_drop(type: str, level: int) -> models.Item:
    """Generate a drop based on type and level."""
    # Calculate drop level as next multiple of 5
    drop_level = next_multiple_of_5(level)
    if type == "weapon":
        item_name = random.choices(
            population=entities.WEAPONS,
            weights=config.WEIGHTS["weapon_drop"][str(drop_level)]
        )[0]
        return models.create_weapon(item_name)
    elif type == "armor":
        item_name = random.choices(
            population=entities.ARMOR,
            weights=config.WEIGHTS["armor_drop"][str(drop_level)]
        )[0]
        return models.create_armor(item_name)
    elif type == "consumable":
        item_name = random.choices(
            population=entities.CONSUMABLES,
            weights=[1 / 3] * 3  # Assuming equal probability for consumables
        )[0]
        return models.create_consumable(item_name)
    else:
        raise ValueError(f"Invalid drop type: {type}")


class Game:
    """
    Main game controller with state management.
    """
    def __init__(self) -> None:
        self.game_over: bool = False
        self.maze: Optional[Maze] = None
        self.storage: Storage = Storage()
        self.player: Optional[entities.Player] = None

    def get_options(self, game_state: str, room: Optional[Room] = None) -> list[str]:
        """
        Get available options based on the provided game state and room type.
        """
        if game_state == 'travel':
            choices: list[str] = room.room_options() if room else []
            if isinstance(room, MonsterRoom) and not room.claimed:
                choices.insert(0, 'Fight monster')
            elif isinstance(room, TreasureRoom) and not room.claimed:
                choices.insert(0, 'Open chest')
            elif isinstance(room, BossRoom) and not room.claimed:
                choices.insert(0, 'Challenge the boss')
            choices.append('View inventory')
            choices.append('Exit to menu')
            return choices
        elif game_state == 'boss':
            return ['Fight boss', 'Go back']
        return []

    def exit_game(self) -> None:
        """Set the game to exit state."""
        self.reset_game_data()
        self.game_over = True

    def start_game(self) -> None:
        """Start a new game with a fresh maze and player."""
        rooms: list[Room] = []
        rooms.append(Room(0))
        for i in range(1, text.maze_size):
            if i % 2 == 0:
                room = MonsterRoom((i + 1), Monsters.keys())
                room.generateMonster()
                room.generateDrops()
                rooms.append(room)
            elif i % 2 == 1:
                rooms.append(TreasureRoom(_id=i + 1, treasure_type="weapon"))
            else:
                rooms.append(Room(i + 1))
        rooms.append(BossRoom(text.maze_size + 1))
        self.maze = Maze(rooms, rooms[0])
        self.maze.generate_maze()
        self.create_player()
        print(text.printing_text_large_spacing)
        text.pretty_print(text.started_text)
        input()
        self.maze.draw_rooms()

    def load_game(self) -> None:
        """Load a saved game from file."""
        rooms: list[Room] = []
        rooms.append(Room(0))
        for i in range(1, text.maze_size):
            if i % 2 == 0:
                room = MonsterRoom((i + 1), Monsters.keys())
                room.generateMonster()
                room.generateDrops()
                rooms.append(room)
            elif i % 2 == 1:
                rooms.append(TreasureRoom(i + 1, treasure_type="weapon"))
            else:
                rooms.append(Room(i + 1))
        rooms.append(BossRoom(text.maze_size + 1))
        for room in rooms:
            if isinstance(room, (TreasureRoom, MonsterRoom, BossRoom)):
                if room.id in self.storage.get_data(config.PLAYER_SAVE_FILE).get("Claimed_rooms", []):
                    room.claimed = True
        self.maze = Maze(rooms, rooms[0])
        self.maze.generate_maze()
        self.load_player()
        print()
        print(text.loaded_text)
        print(text.printing_text_large_spacing)
        input()
        self.maze.draw_rooms()

    def create_player(self) -> None:
        """Create a new player."""
        self.player = entities.create_player()
        self.player.create_new_storage(self.storage, config.PLAYER_SAVE_FILE)

    def load_player(self) -> None:
        """Load player from saved file."""
        atk: int = self.storage.get_data(config.PLAYER_SAVE_FILE).get("Player_attack", text.default_attack)
        current_health: int = self.storage.get_data(config.PLAYER_SAVE_FILE).get("Player_current_health", text.default_health)
        max_health: int = self.storage.get_data(config.PLAYER_SAVE_FILE).get("Player_max_health", text.default_health)
        self.player = entities.create_player()
        self.player.current_health = current_health
        self.player.load_from_storage(self.storage, config.PLAYER_SAVE_FILE)

    def get_player(self) -> Optional[entities.Player]:
        """Get the player object."""
        return self.player

    def load_data(self) -> None:
        """Loader method for data."""
        pass

    def reset_game_data(self) -> None:
        """Reset game data to default values."""
        default_data: dict = self.storage.get_data(config.DEFAULT_SAVE_FILE)
        self.storage.save_data(config.PLAYER_SAVE_FILE, default_data)

    def save_all_data(self, file: str) -> None:
        """Save all current game variables to file."""
        claimed_rooms: list[int] = []
        for room in self.maze.rooms:
            if isinstance(room, (TreasureRoom, MonsterRoom, BossRoom)) and room.claimed:
                if room.id not in self.storage.get_data(file).get("Claimed_rooms", []):
                    claimed_rooms.append(room.id)
        self.storage.save_data(file, {
            "Room_id": self.maze.current_room.id,
            "Claimed_rooms": claimed_rooms
        })
        self.player.save_to_storage(self.storage, file)

    def display_room_info(self) -> None:
        """Display information about the current room based on its type."""
        current_room: Room = self.maze.current_room
        if isinstance(current_room, TreasureRoom):
            print(text.treasure_room_text if not current_room.claimed else text.claimed_treasure_room_text)
        elif isinstance(current_room, MonsterRoom):
            print(text.monster_room_text if not current_room.claimed else text.claimed_monster_room_text)
        elif isinstance(current_room, BossRoom):
            pass

    def fight_boss(self, current_room: BossRoom) -> None:
        """Handle the logic for fighting the boss."""
        command: str = prompt_player_choice(
            preamble=f"You have encountered the boss: {BOSS_NAME}. Do you want to fight this boss?",
            choices=['Fight boss', 'Go back']
        )
        if command in ['exit']:
            self.exit_game()
        elif command in ['go back', 'back']:
            pass
        elif command in ['fight boss', 'fight', 'challenge the boss', 'challenge boss']:
            text.clear_screen()
            monster: entities.Monster = current_room.boss_monster
            input(f"You have encountered {BOSS_NAME}.\n Atk: {monster.attack}, HP: {monster.max_health}\nPress enter to continue...")
            text.clear_screen()
            combat_seq: CombatSequence = CombatSequence(self.player, monster, 3, 20)
            result: str = combat_seq.start_boss_sequence()
            if result == 'victory':
                current_room.claimed = True
                self.save_all_data(config.PLAYER_SAVE_FILE)
                print('You have defeated the boss! Congratulations on completing the game!')
                input('Press enter to exit.')
            elif result == 'defeat':
                command = prompt_player_choice(
                    preamble="You have been defeated by the boss. Game over.",
                    choices=['Fight boss', 'Go back']
                )
                if command in ['exit', 'retry', 'start', 'play']:
                    self.exit_game()

    def use_item(self, item_name: str) -> None:
        """Handle the logic for using an item."""
        if item_name == 'health potion':
            magnitude: float = self.player.max_health * 0.2
            self.player.current_health = min(self.player.current_health + magnitude, self.player.max_health)
            print('\n' + text.equip_spacing_text)
            print(f"You have healed {magnitude} health!")
            print(text.equip_spacing_text + '\n')
        elif item_name == 'attack potion':
            magnitude: float = self.player.attack * 0.2
            self.player.attack += magnitude
            print('\n' + text.equip_spacing_text)
            print(f'Your attack has increased by {magnitude}!')
            print(text.equip_spacing_text + '\n')
        input("\nPress enter to continue...")

    def command_exit(self) -> None:
        """Handle the quit/exit command."""
        self.exit_game()

    def command_enter_boss_chamber(self) -> None:
        """Handle the enter boss chamber command."""
        self.maze.travel_to('boss chamber')
        self.maze.draw_rooms()

    def command_view_inventory(self) -> None:
        """Handle the view inventory command."""
        end_loop: bool = False
        while not end_loop:
            text.clear_screen()
            command: str = prompt_player_choice(
                preamble=self.player.return_stats(),
                choices=['Use item', 'Go back']
            )
            if command in ['use item']:
                item_name: str = text.prompt_player_choice(
                    preamble="Please enter the name of the item you want to use:",
                    choices=self.player.inventory.list_items()
                )
                if self.player.inventory.use_item(item_name):
                    self.use_item(item_name)
                else:
                    print(text.input_error_prompt)
                    input("\nPress enter to continue...")
            else:
                end_loop = True

    def command_go_direction(self, direction: str) -> None:
        """Handle the go direction command."""
        if direction in text.directions:
            self.maze.travel_to(direction)
            self.save_all_data(config.PLAYER_SAVE_FILE)
        else:
            print(text.input_error_prompt)

    def command_open_chest(self) -> None:
        """Handle the open chest command."""
        current_room = self.maze.current_room
        if isinstance(current_room, TreasureRoom):
            # Open chest logic
            treasure_type: str = current_room.get_type()
            dropped_item = generate_drop(treasure_type, current_room.id)
            if treasure_type in ['weapon', 'armour']:
                print('\n' + text.equip_spacing_text)
                if isinstance(dropped_item, models.Weapon):
                    print(
                        f"You have found a {dropped_item.name} (atk: {dropped_item.attack_bonus})!"
                    )
                elif isinstance(dropped_item, models.Armor):
                    print(
                        f"You have found {dropped_item.name} (slot: {type(dropped_item).__name__}, def: {dropped_item.defense_bonus})!"
                    )
                print(text.equip_spacing_text + '\n')

                command: str = prompt_player_choice(
                    preamble=text.equip_spacing_text,
                    choices=['Equip item', 'Go back']
                )
                if command in ['go back', 'back']:
                    pass
                elif command in ['equip item', 'equip']:
                    self.player.equip(dropped_item)
                    input('\nPress enter to continue...')
                    self.maze.current_room.claimed = True
            elif treasure_type == 'consumable':
                self.player.inventory.add_item(drop)
                print('\n' + text.equip_spacing_text)
                print('You have obtained a ' + drop + '!')
                command = prompt_player_choice(
                    preamble=text.equip_spacing_text,
                    choices=['Consume item', 'Go back']
                )
                if command in ['go back', 'back']:
                    pass
                elif command in ['consume item', 'consume']:
                    if drop in Consumable:
                        if self.player.inventory.use_item(drop):
                            self.use_item(drop)
                        else:
                            print(text.input_error_prompt)
                    else:
                        print(text.input_error_prompt)
                self.maze.current_room.drop = None
                self.maze.current_room.claimed = True

    def command_fight(self) -> None:
        """Handle the fight command."""
        text.clear_screen()
        monster: entities.Monster = entities.create_monster(self.maze.current_room.monster)
        input(f"You have encountered a {self.maze.current_room.monster}.\n Atk: {monster.attack}, HP: {monster.max_health}\nPress enter to continue...")
        text.clear_screen()
        combat_seq: CombatSequence = CombatSequence(self.player, monster, 3, 20)
        result: str = combat_seq.start_sequence()
        if result == 'victory':
            current_room: Room = self.maze.current_room
            current_room.monster = None
            current_room.claimed = True

            drop: str = current_room.drop
            if drop.type == 'weapon':
                print(f"You have obtained a {drop.drop}({text.Weapon[drop.drop]})!")
            elif drop.type == 'armour':
                slot: str = text.ArmourSlots[drop.drop]
                print(f"You have obtained {drop.drop} (slot: {slot}, def: {text.Armour[drop.drop]})!")
            command = prompt_player_choice(
                preamble="What would you like to do?",
                choices=['Equip item', 'Go back']
            )
            if command in ['go back', 'back']:
                pass
            elif command in ['equip item', 'equip']:
                if drop.drop in text.Weapon:
                    self.player.inventory.equip_weapon(drop.drop)
                    self.player.recalculate_stats()
                    self.save_all_data(config.PLAYER_SAVE_FILE)
                    input('\nPress enter to continue...')
                elif drop.drop in text.Armour:
                    slot = text.ArmourSlots[drop.drop]
                    self.player.inventory.equip_armour(slot, drop.drop)
                    self.player.recalculate_stats()
                    self.save_all_data(config.PLAYER_SAVE_FILE)
                    input('\nPress enter to continue...')
            self.player.recalculate_stats()
            self.save_all_data(config.PLAYER_SAVE_FILE)
        elif result == 'defeat':
            command = prompt_player_choice(
                preamble=(
                    "You have been defeated by the monster. Game over.\n"
                    "Do you want to retry?"
                ),
                choices=['Retry', 'Exit to Menu']
            )
            if command in ['quit', 'exit']:
                self.command_exit()
            elif command in ['retry', 'start', 'play']:
                self.game_over = True

    def handle_command(self, command: str) -> None:
        """Handle a single command based on user input."""
        if command in ['quit', 'exit']:
            self.command_exit()
        elif command == 'enter boss chamber' or command.startswith('enter boss'):
            self.command_enter_boss_chamber()
        elif command in ['view inventory', 'inventory', 'inv']:
            self.command_view_inventory()
        elif command.startswith('go'):
            direction: str = command.split()[1]
            self.command_go_direction(direction)
        elif command.startswith('open'):
            self.command_open_chest()
        elif command.startswith('fight'):
            self.command_fight()
        else:
            raise ValueError("Invalid command")

    def run(self) -> None:
        """Main game loop - handles user input and game state."""

        while not self.game_over:
            text.clear_screen()
            self.maze.draw_rooms()

            # Display room-specific text
            self.display_room_info()

            # Main command processing
            command: str = prompt_player_choice(
                preamble="What would you like to do?",
                choices=self.maze.current_room.room_options()
            )
            self.handle_command(command)
