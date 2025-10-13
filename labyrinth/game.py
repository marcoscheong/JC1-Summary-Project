# Game module - Game controller and main loop (UI + game logic combined)

import random
from typing import Optional

from labyrinth import config, entities, maze, models, storage, text
from labyrinth.storage import Storage
from labyrinth.maze import Room, TreasureRoom, MonsterRoom, BossRoom, Maze
from labyrinth.combat import CombatSequence
from labyrinth.text import prompt_player_choice

BOSS_NAME = "Origin of Chaos"


def save_game_data(game: 'Game') -> None:
    """Save the current game state to a file."""
    data = game.to_dict()
    storage.save_to_json(config.PLAYER_SAVE_FILE, data)


def load_game_data() -> dict:
    """Load game state from a file."""
    return storage.load_from_json(config.PLAYER_SAVE_FILE)


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


def is_monster_boss(monster: entities.Monster) -> bool:
    """Check if a monster is the boss."""
    return monster.name == BOSS_NAME


class Game:
    """Main game controller with state management."""

    def __init__(self,
                 maze_: Optional[maze.Maze] = None,
                 current_room_id: Optional[int] = None,
                 player: Optional[entities.Player] = None) -> None:
        self.game_over: bool = False
        self.maze = maze_ or maze.generate_maze()
        self.storage: Storage = Storage()
        self.player = player or entities.create_player()
        self.current_room = (
            self.maze.get_by_id(current_room_id) if current_room_id
            else self.maze.get_start_room()
        )

    def get_options(self, room: Optional[Room] = None) -> list[str]:
        """Get available options based on the provided game state and room type."""
        choices: list[str] = room.get_options() if room else []
        choices.append('View inventory')
        choices.append('Exit to menu')
        return choices

    def start_game(self) -> None:
        """Start the game."""
        print(text.printing_text_large_spacing)
        text.pretty_print(text.started_text)
        input()
        self.maze.draw_rooms(self.current_room)

    def save_game(self) -> None:
        """Save the current game state to player file."""
        save_game_data(self)
        print("Game saved.")

    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """Create a Game instance from a dictionary."""
        game = cls(
            maze_=Maze.from_dict(data["maze"]),
            current_room_id=data["current_room_id"],
            player=entities.Player.from_dict(data["player"]),
        )
        return game

    @classmethod
    def load_from_data(cls) -> 'Game':
        """Load a game from saved data."""
        data = load_game_data()
        game = cls.from_dict(data)
        return game

    def create_player(self) -> None:
        """Create a new player."""
        self.player = entities.create_player()

    def display_room_info(self) -> None:
        """Display information about the current room based on its type."""
        current_room: Room = self.current_room
        if isinstance(current_room, TreasureRoom):
            print(text.treasure_room_text if not current_room.completed else text.completed_treasure_room_text)
        elif isinstance(current_room, MonsterRoom):
            print(text.monster_room_text if not current_room.completed else text.completed_monster_room_text)
        elif isinstance(current_room, BossRoom):
            pass

    def lose_fight(self, monster: Optional[entities.Monster]) -> bool | None:
        """Handle losing a fight."""
        print(text.defeat_text)
        if monster and is_monster_boss(monster):
            reason = f"You have been defeated by the boss."
        elif monster:
            reason = f"You have been defeated by {monster.name}."
        else:
            reason = f"You lost."
        command = prompt_player_choice(
            preamble=(
                f"{reason} Game over.\n"
                "Do you want to retry?"
            ),
            choices=['Retry', 'Exit to Menu']
        )
        return self.handle_command(command)

    def win_fight(self, monster: entities.Monster) -> bool | None:
        """Handle winning a fight."""
        if is_monster_boss(monster):
            print('You have defeated the boss! Congratulations on completing the game!')
            text.prompt_continue("Press enter to exit.")
            return self.command_exit()
        else:
            current_room = self.current_room
            assert isinstance(current_room, MonsterRoom), f"{current_room} is not a monster room."
            print(text.victory_text)
            current_room.complete()
            dropped_item = generate_drop(
                type=random.choice(['weapon', 'armour']),
                level=current_room.id
            )
            self.command_pickup(dropped_item)

    def consume_item(self, item_name: str) -> None:
        """Handle the logic for using an item."""
        assert item_name in models.CONSUMABLES, f"{item_name} is not a consumable."
        if item_name == 'health potion':
            healAmount = self.player.heal(self.player.max_health * 0.2)
            text.pull_quote(
                f"You have healed {healAmount} health!",
                divider=text.equip_divider
            )
        elif item_name == 'attack potion':
            strengthenAmount = self.player.strengthen(self.player.attack * 0.2)
            text.pull_quote(
                f"Your attack has increased by {strengthenAmount}!",
                divider=text.equip_divider
            )
        text.linebreak()
        text.prompt_continue()

    def command_exit(self) -> bool:
        """Handle the quit/exit command (no retry)."""
        return False

    def command_retry(self) -> bool:
        """Handle the retry command."""
        return True

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
                    preamble="Which item do you want to use?",
                    choices=list(
                        self.player.inventory.list_items("Consumables")
                    )
                )
                if self.player.inventory.use_item(item_name):
                    self.consume_item(item_name)
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

    def command_equip(self, item: Optional[models.Item] = None) -> None:
        """Equip an item."""
        if item is None:
            item_name: str = text.prompt_player_choice(
                preamble="Which item do you want to equip?",
                choices=list(
                    self.player.inventory.list_items("Weapons")
                ) + list(
                    self.player.inventory.list_items("Armor")
                )
            )
            item = self.player.inventory.use_item(item_name)
            assert item is not None, f"{item_name} was not in inventory."
        if isinstance(item, (models.Weapon, models.Armor)):
            if self.player.equip(item):
                text.pull_quote(f"{item.name} equipped.", divider=text.equip_divider)
            else:
                print(f"Failed to equip {item.to_string()}.")
        else:
            print(f"{item.name} cannot be equipped.")
            self.player.inventory.add_item(item.name)
        text.linebreak()
        text.prompt_continue()

    def command_pickup(self, dropped_item: models.Item) -> None:
        """Handle the pickup command."""
        current_room = self.current_room
        assert isinstance(current_room, (TreasureRoom, MonsterRoom)), f"{current_room} is not a treasure room or monster room."
        text.pull_quote(
            f"You have found a {dropped_item.to_string()}",
            divider=text.equip_divider
        )
        if isinstance(dropped_item, (models.Weapon, models.Armor)):
            command: str = prompt_player_choice(
                preamble="What do you want to do?",
                choices=['Equip item', 'Leave it']
            )
            if command in ['leave']:
                return None
            elif command in ['equip item', 'equip']:
                self.command_equip(dropped_item)
                current_room.complete()
        elif isinstance(dropped_item, models.Potion):
            command = prompt_player_choice(
                preamble="What do you want to do?",
                choices=['Consume item', 'Take it', 'Leave it']
            )
            if command in ['leave']:
                return None
            elif command in ['consume item', 'consume']:
                self.consume_item(dropped_item.name)
                current_room.complete()
            elif command in ['take it', 'take']:
                self.player.inventory.add_item(dropped_item.name)
                current_room.complete()

    def command_open_chest(self) -> None:
        """Handle the open chest command."""
        current_room = self.current_room
        assert isinstance(current_room, TreasureRoom), f"{current_room} is not a treasure room."
        # Open chest logic
        treasure_type: str = current_room.get_type()
        dropped_item = generate_drop(treasure_type, current_room.id)
        self.command_pickup(dropped_item)
        current_room.complete()

    def command_fight(self) -> bool | None:
        """Fight the monster in the current room."""
        current_room = self.current_room
        assert isinstance(current_room, MonsterRoom), f"{current_room} is not a monster room."
        monster = current_room.monster
        assert monster is not None, f"{current_room} has no monster to fight."
        text.clear_screen()
        text.prompt_continue(
            f"You have encountered a {monster.to_string()}.\n"
            "Press enter to continue..."
        )
        text.clear_screen()
        combat_seq: CombatSequence = CombatSequence(
            player=self.player,
            monster=monster,
            base_elixir=3,
            max_turns=20
        )
        if is_monster_boss(monster):
            victor = combat_seq.run_combat(
                elixir_steal=True,
                shared_fate=0.25
            )
        else:
            victor = combat_seq.run_combat()

        if isinstance(victor, entities.Player):
            return self.win_fight(monster)
        elif isinstance(victor, entities.Monster):
            return self.lose_fight(monster)

    def handle_command(self, command: str) -> bool | None:
        """Handle a single command based on user input."""
        if command in ['quit', 'exit']:
            return self.command_exit()
        elif command in ['retry', 'start', 'play']:
            return self.command_retry()
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
            return self.command_fight()
        else:
            raise ValueError("Invalid command")

    def to_dict(self) -> dict:
        """Return a dictionary representation of the game state."""
        return {
            "player": self.player.to_dict(),
            "maze": self.maze.to_dict(),
            "current_room_id": self.current_room.id,
            "game_over": self.game_over
        }

    def run(self) -> bool:
        """Main game loop - handles user input and game state.
        
        Returns True if the user wants to retry, False if they want to exit to menu.
        """
        self.start_game()
        play_game = True
        while play_game != False:
            text.clear_screen()
            self.maze.draw_rooms(self.current_room)

            # Display room-specific text
            self.display_room_info()

            # Main command processing
            command: str = prompt_player_choice(
                preamble="What would you like to do?",
                choices=self.current_room.get_options()
            )
            # A False value for play_game indicates the user wants to exit
            play_game = self.handle_command(command)
        return play_game
