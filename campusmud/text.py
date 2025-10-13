import select
import sys
import os
import time
from campusmud.data import load_game_data

game_data = load_game_data()

Monsters = {name: {"max_health": data["max_health"], "attack": data["attack"]} for name, data in game_data["monsters"].items()}
Consumable = game_data["items"]["consumables"]
Armour = game_data["items"]["armor"]
Weapon = game_data["items"]["weapons"]

Game_name = "Labyrinth Ascension"
Game_info = [
    "Explore Maze Rooms: Each maze run is procedurally generated (different layouts each time).",
    "Rooms contain enemies, puzzles, traps, or treasure.",
    "Fight Enemies: Defeat enemies to gain EXP and Rank Points.",
    "Enemies drop loot (weapons, health, buffs).",
    "Level Up & Rank Up: EXP increases your Level (boosts stats like health, speed, attack).",
    "Rank Points increase your Rank Tier (unlocks new abilities).",
    "Progressive Difficulty: Higher ranks unlock deeper maze layers with harder enemies and better rewards.",
    "Death & Respawn: If you die, you respawn at your base camp with your rank intact but lose temporary loot."
]


Game_lore = [
    "In a world where warriors prove themselves in an endless shifting labyrinth, your journey starts at rock bottom.",
    "Climb the ranks, earn your place among legends, and uncover the secret of the maze — a truth that might change everything."
]
room_types = ['treasure', 'monster']

maze_size = 36

welcome_prompt = "Welcome to Labyrinth Ascension, a Single Player MUD game. Do you want to start or load your game?"
started_text = 'In this world of labyrinths, you have arrived in the top-most level.\nBegin your descent to the lowest level to uncover the long lost secrets of this labyrinth. \n\nTo select an option, type out the number of your choice or the full command.\nE.g. "1", or "Go down".\nWhen you want to continue to the next scene, press the "Enter" key to procede.\n'
treasure_room_text = 'You have entered a room containing treasure. Do you want to open the chest or travel to another room?'
claimed_treasure_room_text = 'You have entered a room containing an empty chest. Do you want to travel to another room?'
monster_room_text = 'You have encountered a monster. Do you want to fight this monster?'
claimed_monster_room_text = 'You have entered a room containing an empty monster lair. Do you want to travel to another room?'
loaded_text = "Game loaded successfully!"
load_error_text = "No saved game found. Starting a new game instead."
how_to_play_text = (
    "How to Play: Labyrinth Ascension\n\n"
    "1. Objective\n"
    "   - Explore the labyrinth\n"
    "   - Defeat monsters\n"
    "   - Collect loot\n\n"
    "2. Navigation\n"
    "   - Move with commands like 'go up', 'go down', etc.\n"
    "   - You may also use numbers to select your command\n"
    "   - Rooms may contain treasure, monsters, or be empty\n"
    "   - Goal: reach the bottom-right corner to face the final boss\n\n"
    "3. Combat (turn-based)\n"
    "   Commands:\n"
    "     attack : deal 1 damage per elixir spent\n"
    "     shield : block 1 damage per elixir spent\n"
    "     heal   : restore 1 health per elixir spent\n"
    "     save   : keep 1 elixir for the next round\n\n"
    "   Mechanics:\n"
    "   - Elixir is your combat resource\n"
    "   - Each magnitude costs 1 elixir\n"
    "     (e.g. attack x2 = 2 attacks = 2 elixir)\n"
    "   - Magnitude = number of times a move is applied\n"
)


input_prompt = "Please select a choice: "
input_error_prompt = "Please input again."

combat_sequence_prompt = "Here are your available moves: "
ability_addition_error = "Please input a valid ability name"
magnitude_prompt = "Please input the magnitude of ability: "

successful_room_travel = "You have travelled to room with ID: "
thanks_message = "Thanks for playing!"

directions = ['up', 'down', 'left', 'right']

printing_text_spacing = '\n=================== \n'

# Dictionary of all combinations
rooms = {
    "N":    " │ ",
    "S":    " │ ",
    "E":    "── ",
    "W":    " ──",
    "NS":   " │ ",
    "NE":   " └─",
    "NW":   "─┘ ",
    "SE":   " ┌─",
    "SW":   "─┐ ",
    "EW":   "───",
    "NSE":  " ├─",
    "NSW":  "─┤ ",
    "NEW":  "─┴─",
    "SEW":  "─┬─",
    "NSEW": "─┼─",
    "BOSS": " ⬢ ",
}

player_rooms = {
    "N":    " O ",
    "S":    " O ",
    "E":    "─O ",
    "W":    " O─",
    "NS":   " O ",
    "NE":   " O─",
    "NW":   "─O ",
    "SE":   " O─",
    "SW":   "─O ",
    "EW":   "─O─",
    "NSE":  " O─",
    "NSW":  "─O ",
    "NEW":  "─O─",
    "SEW":  "─O─",
    "NSEW": "─O─",
    "BOSS": " ⬢ ",
}

move_pool = ['attack', 'shield', 'heal', 'save']

monster_ability_weights = [20, 4, 3, 6]

weaponweights5  = [50, 40, 35, 30, 25, 20, 15, 10, 8, 5, 3, 2, 1, 1, 1]
weaponweights10 = [40, 35, 30, 28, 25, 20, 15, 12, 10, 8, 5, 3, 2, 1, 1]
weaponweights15 = [30, 28, 25, 22, 20, 18, 15, 12, 10, 8, 5, 3, 2, 2, 1]
weaponweights20 = [20, 18, 15, 12, 10, 10, 12, 15, 18, 20, 25, 30, 35, 25, 15]
weaponweights25 = [5, 5, 5, 5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 40, 35]

armourweights5 =  [50, 50, 50, 50, 40, 40, 40, 40, 25, 25, 25, 25, 15, 15, 15, 15, 10, 10, 10, 10]
armourweights10 = [40, 40, 40, 40, 35, 35, 35, 35, 25, 25, 25, 25, 15, 15, 15, 15, 10, 10, 10, 10]
armourweights15 = [35, 35, 35, 35, 30, 30, 30, 30, 25, 25, 25, 25, 20, 20, 20, 20, 15, 15, 15, 15]
armourweights20 = [30, 30, 30, 30, 28, 28, 28, 28, 25, 25, 25, 25, 23, 23, 23, 23, 20, 20, 20, 20]
armourweights25 = [20, 20, 20, 20, 22, 22, 22, 22, 25, 25, 25, 25, 28, 28, 28, 28, 30, 30, 30, 30]

boss_monster = "Origin of Chaos"

victory_text = "You have defeated the monster!"
defeat_text = "You have been defeated by the monster..."

printing_text_large_spacing = '\n══════════════ • ══════════════ \n'
combat_spacing_text = '────── ◈ ──────'
ability_spacing_text = '··─··'
equip_spacing_text = "───┈───"


def clear_screen() -> None:
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_number(x: int | float, places: int = 1) -> int | float:
    """Format numbers to 1 decimal if needed, no trailing .0."""
    return int(x) if isinstance(x, (int, float)) and float(x).is_integer() else round(x, places)


def health_bar(current: int,
               maximum: int,
               bar_length: int = 20,
               char_filled: str = '█',
               char_empty: str = '-') -> str:
        """Return a string representing a health bar."""
        if maximum <= 0:
            ratio = 0
        else:
            ratio = current / maximum
        filled_length = int(bar_length * ratio)
        bar = (
            (char_filled * filled_length)
            + (char_empty * (bar_length - filled_length))
        )
        return f"[{bar}] {current}/{maximum}"


def pretty_print(text_content):
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


def linebreak() -> None:
    """Print a line break for better readability."""
    print()


def prompt_player_choice(
        preamble: str,
        choices: list[str],
        prompt: str = "Enter your choice: "
) -> str:
    """Display choices and prompt the player for a valid choice.

    Returns the valid choice selected by the player.
    """
    print(preamble)
    for i, option in enumerate(choices):
        print(f'{(i + 1)}. {option}')
        time.sleep(0.05)
    choice = input(prompt).strip()
    while not choice.isdecimal() or not (1 <= int(choice) <= len(choices)):
        print("Please enter a valid choice.")
        choice = input(prompt).strip()
    return choices[int(choice) - 1]


def prompt_number_input(
        prompt: str,
        min_value: int,
        max_value: int
) -> int:
    """Prompt the player for a number input within a specified range.

    Returns the valid number input by the player.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input.isdecimal():
            number = int(user_input)
            if min_value <= number <= max_value:
                return number
        print(f"Please enter a number between {min_value} and {max_value}.")


def prompt_continue(prompt: str = "Press Enter to continue...") -> None:
    """Prompt the player to press Enter to continue."""
    input(prompt)