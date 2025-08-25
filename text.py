import mud

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

maze_size = 15

player_save_file = "player_data.json"

welcome_prompt = "Welcome to Labyrinth Ascension, a Single Player MUD game. Do you want to start or load your game?"
start_choices = ['start', 'quit', 'load']
started_text = 'In this world of labyrinths, you have arrived in the top-most level.\nBegin your descent to the lowest level to uncover the long lost secrets of this labyrinth. \n\nTo select an option, type out the number of your choice or the full command.\nE.g. "1", or "Go down".\n'
treasure_room_text = 'You have entered a room containing treasure. Do you want to open the chest or travel to another room?'
monster_room_text = 'You have encountered a monster. Do you want to fight this monster?'

input_prompt = "Please select a choice: "
input_error_prompt = "Please input again."

combat_sequence_prompt = "Here are your available moves: "
ability_addition_error = "Please input a valid ability name"
magnitude_prompt = "Please input the magnitude of ability: "
cheapest_ability_cost = 1

successful_room_travel = "You have travelled to room with ID: "
thanks_message = "Thanks for playing!"

directions = ['up', 'down', 'left', 'right']

printing_text_spacing = '\n=================== \n'

# Dictionary of all combinations
rooms = {
    "N": """
 │ 
 · 
""",
    "S": """
 · 
 │ 
""",
    "E": """
 ·─
""",
    "W": """
─· 
""",
    "NS": """
 │ 
 · 
 │ 
""",
    "NE": """
 │ 
 ·─
""",
    "NW": """
 │ 
─· 
""",
    "SE": """
 ·─
 │ 
""",
    "SW": """
─· 
 │ 
""",
    "EW": """
─·─
""",
    "NSE": """
 │ 
 ·─
 │ 
""",
    "NSW": """
 │ 
─· 
 │ 
""",
    "NEW": """
 │ 
─·─
""",
    "SEW": """
─·─
 │ 
""",
    "NSEW": """
 │ 
─·─
 │ 
"""
}

player_rooms = {
    "N": """
 │ 
 O 
""",
    "S": """
 O 
 │ 
""",
    "E": """
 O─
""",
    "W": """
─O 
""",
    "NS": """
 │ 
 O 
 │ 
""",
    "NE": """
 │ 
 O─
""",
    "NW": """
 │ 
─O 
""",
    "SE": """
 O─
 │ 
""",
    "SW": """
─O 
 │ 
""",
    "EW": """
─O─
""",
    "NSE": """
 │ 
 O─
 │ 
""",
    "NSW": """
 │ 
─O 
 │ 
""",
    "NEW": """
 │ 
─O─
""",
    "SEW": """
─O─
 │ 
""",
    "NSEW": """
 │ 
─O─
 │ 
"""
}

move_pool = ['attack', 'shield', 'heal', 'save']

default_health = 15
default_attack = 10

Monsters = {
    "Slime": [10, 10],
    "Pig": [15, 15],
    "Hog": [20, 20],
    "Goblin": [50, 30],
    "Wolf": [80, 40],
    "Orc": [150, 80],
    "Skeleton": [120, 60],
    "Zombie": [200, 70],
    "Bandit": [250, 100],
    "Giant Spider": [300, 120],
    "Dark Knight": [500, 200],
    "Stone Golem": [800, 300],
    "Troll": [1000, 350],
    "Wyvern": [1500, 500],
    "Minotaur": [2000, 600],
    "Hydra": [3000, 800],
    "Ancient Treant": [4000, 900],
    "Fire Drake": [5000, 1200],
    "Shadow Reaper": [6000, 1500],
    "Frost Titan": [7000, 1700],
    "Chaos Serpent": [8000, 2000],
    "Demon Lord": [9000, 2500],
    "Elder Dragon": [10000, 3000]
  }

printing_text_large_spacing = '\n══════════════ • ══════════════ \n'
combat_spacing_text = '────── ◈ ──────'
ability_spacing_text = '··─··'
