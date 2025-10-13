# Game module - Game controller and main loop (UI + game logic combined)

import random
from typing import Optional

from labyrinth import config, entities, maze, models, text
from labyrinth.storage import Storage
from labyrinth.maze import Room, TreasureRoom, MonsterRoom, BossRoom, Maze
from labyrinth.combat import CombatSequence
from labyrinth.text import prompt_player_choice

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
            population=models.WEAPONS,
            weights=config.WEIGHTS["weapon_drop"][str(drop_level)]
        )[0]
        return models.create_weapon(item_name)
    elif type == "armor":
        item_name = random.choices(
            population=models.ARMOR,
            weights=config.WEIGHTS["armor_drop"][str(drop_level)]
        )[0]
        return models.create_armor(item_name)
    elif type == "consumable":
        item_name = random.choices(
            population=models.CONSUMABLES,
            weights=[1 / 3] * 3  # Assuming equal probability for consumables
        )[0]
        return models.create_consumable(item_name)
    else:
        raise ValueError(f"Invalid drop type: {type}")


class Game:
    """Main game controller with state management."""

    def __init__(self) -> None:
        self.game_over: bool = False
        self.maze = maze.generate_maze()
        self.storage: Storage = Storage()
        self.player = entities.create_player()
        self.current_room = self.maze.get_start_room()

    def get_options(self, room: Optional[Room] = None) -> list[str]:
        """Get available options based on the provided game state and room type."""
        choices: list[str] = room.get_options() if room else []
        choices.append('View inventory')
        choices.append('Exit to menu')
        return choices

    def exit_game(self) -> None:
        """Set the game to exit state."""
        self.reset_game_data()
        self.game_over = True

    def start_game(self) -> None:
        """Start a new game with a fresh maze and player."""
        print(text.printing_text_large_spacing)
        text.pretty_print(text.started_text)
        input()
        self.maze.draw_rooms(self.current_room)

    def load_game(self) -> None:
        """Load a saved game from file."""
        rooms: list[Room] = []
        rooms.append(Room(0))
        for i in range(1, config.MAZE_SIZE):
            if i % 2 == 0:
                room = MonsterRoom((i + 1), entities.MONSTERS)
                room.generateMonster()
                rooms.append(room)
            elif i % 2 == 1:
                rooms.append(TreasureRoom(i + 1, treasure_type="weapon"))
            else:
                rooms.append(Room(i + 1))
        rooms.append(BossRoom(config.MAZE_SIZE + 1))
        for room in rooms:
            if isinstance(room, (TreasureRoom, MonsterRoom, BossRoom)):
                if room.id in self.storage.get_data(config.PLAYER_SAVE_FILE).get("Claimed_rooms", []):
                    room.complete()
        self.maze = Maze(rooms, rooms[0])
        self.maze.connect_rooms()
        self.load_player()
        print()
        print(text.loaded_text)
        print(text.printing_text_large_spacing)
        input()
        self.maze.draw_rooms(self.current_room)

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
            if isinstance(room, (TreasureRoom, MonsterRoom, BossRoom)) and room.completed:
                if room.id not in self.storage.get_data(file).get("Claimed_rooms", []):
                    claimed_rooms.append(room.id)
        self.storage.save_data(file, {
            "Room_id": self.current_room.id,
            "Claimed_rooms": claimed_rooms
        })
        self.player.save_to_storage(self.storage, file)

    def display_room_info(self) -> None:
        """Display information about the current room based on its type."""
        current_room: Room = self.current_room
        if isinstance(current_room, TreasureRoom):
            print(text.treasure_room_text if not current_room.completed else text.completed_treasure_room_text)
        elif isinstance(current_room, MonsterRoom):
            print(text.monster_room_text if not current_room.completed else text.completed_monster_room_text)
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
            monster: entities.Monster = current_room.monster
            input(f"You have encountered {BOSS_NAME}.\n Atk: {monster.attack}, HP: {monster.max_health}\nPress enter to continue...")
            text.clear_screen()
            combat_seq: CombatSequence = CombatSequence(
                player=self.player,
                monster=monster,
                base_elixir=3,
                max_turns=20
            )
            victor = combat_seq.run_combat(
                elixir_steal=True,
                shared_fate=0.25
            )
            if isinstance(victor, entities.Player):
                current_room.complete()
                self.save_all_data(config.PLAYER_SAVE_FILE)
                print('You have defeated the boss! Congratulations on completing the game!')
                text.prompt_continue("Press enter to exit.")
            elif isinstance(victor, entities.Monster):
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
        text.linebreak()
        text.prompt_continue()

    def command_exit(self) -> None:
        """Handle the quit/exit command."""
        self.exit_game()

    def command_enter_boss_chamber(self) -> None:
        """Handle the enter boss chamber command."""
        self.command_go_direction('boss chamber')
        self.maze.draw_rooms(self.current_room)

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
                    text.linebreak()
                    text.prompt_continue()
            else:
                end_loop = True

    def command_go_direction(self, direction: str) -> None:
        """Handle the go direction command."""
        current_room = self.current_room
        # Handle special boss room access
        if direction == 'boss chamber' or direction == 'boss':
            # Find if current room connects to boss room
            current_room = self.current_room
            boss_direction = current_room.get_boss_direction()
            if not boss_direction:
                print("You cannot access the Boss Chamber from here.")
            else:
                self.command_go_direction(boss_direction)
        
        # Regular movement
        go_room = current_room.get_room(direction)
        if go_room is not None:
            self.current_room = go_room
            if isinstance(go_room, BossRoom):
                print("You enter the foreboding Boss Chamber...")
            else:
                print(text.successful_room_travel + str(go_room.id))

    def command_open_chest(self) -> None:
        """Handle the open chest command."""
        current_room = self.current_room
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
                    text.linebreak()
                    text.prompt_continue()
                    self.current_room.complete()
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
                self.current_room.drop = None
                self.current_room.complete()

    def command_fight(self) -> None:
        """Handle the fight command."""
        text.clear_screen()
        monster: entities.Monster = entities.create_monster(self.current_room.monster)
        input(f"You have encountered a {self.current_room.monster}.\n Atk: {monster.attack}, HP: {monster.max_health}\nPress enter to continue...")
        text.clear_screen()
        combat_seq: CombatSequence = CombatSequence(self.player, monster, 3, 20)
        victor = combat_seq.run_combat()
        if isinstance(victor, entities.Player):
            print(text.victory_text)
            current_room: Room = self.current_room
            current_room.monster = None
            current_room.complete()

            dropped_item = generate_drop(
                type=random.choice(['weapon', 'armour']),
                level=current_room.id
            )
            print(f"You have obtained a {dropped_item.name}!")
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
                    text.linebreak()
                    text.prompt_continue()
                elif drop.drop in text.Armour:
                    slot = text.ArmourSlots[drop.drop]
                    self.player.inventory.equip_armour(slot, drop.drop)
                    self.player.recalculate_stats()
                    self.save_all_data(config.PLAYER_SAVE_FILE)
                    text.linebreak()
                    text.prompt_continue()
            self.player.recalculate_stats()
            self.save_all_data(config.PLAYER_SAVE_FILE)
        elif isinstance(victor, entities.Monster):
            print(text.defeat_text)
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
            self.maze.draw_rooms(self.current_room)

            # Display room-specific text
            self.display_room_info()

            # Main command processing
            command: str = prompt_player_choice(
                preamble="What would you like to do?",
                choices=self.current_room.get_options()
            )
            self.handle_command(command)
