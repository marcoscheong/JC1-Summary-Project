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

maze_size = 24

player_save_file = "player_data.json"

welcome_prompt = "Welcome to Labyrinth Ascension, a Single Player MUD game. Do you want to start or load your game?"
start_choices = ['start', 'quit', 'load']
started_text = 'In this world of labyrinths, you have arrived in the top-most level.\nBegin your descent to the lowest level to uncover the long lost secrets of this labyrinth. \n\nTo select an option, type out the number of your choice or the full command.\nE.g. "1", or "Go down".\nWhen you want to continue to the next scene, press the "Enter" key to procede.\n'
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
}

move_pool = ['attack', 'shield', 'heal', 'save']

monster_ability_weights = [20, 4, 3, 6]



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


Weapon = {
  "Fist": 1,
  "Beginner Daggers": 2,
  "Beginner Wand": 3,
  "Wooden Sword": 5,
  "Intermediate Daggers": 7,
  "Intermediate Wand": 8,
  "Knucklebust": 10,
  "Stone Sword": 20,
}

Armour = {
  "Leather Leggings": 1,
  "Leather Boots": 1,
  "Leather Helmet": 1,
  "Leather Chestplate": 1,
  "Chainmail Leggings": 5,
  "Chainmail Boots": 5,
  "Chainmail Helmet": 5,
  "Chainmail Chestplate": 5,
  "Iron Leggings": 25,
  "Iron Boots": 25,
  "Iron Helmet": 25,
  "Iron Chestplate": 25,
  "Diamond Leggings": 50,
  "Diamond Boots": 50,
  "Diamond Helmet": 50,
  "Diamond Chestplate": 50,
  "Draconic Leggings": 300,
  "Draconic Boots": 300,
  "Draconic Helmet": 300,
  "Draconic Chestplate": 300
}

weaponweights5 = [50, 40, 30, 25, 20, 15, 10, 5]
weaponweights10 = [40, 30, 30, 30, 20, 15, 10, 10]
weaponweights15 = [25, 25, 30, 30, 25, 25, 20, 15]
weaponweights20 = [10, 10, 15, 15, 20, 20, 25, 30]
weaponweights25 = [5, 5, 10, 10, 15, 15, 20, 25]

armourweights5 = [50, 50, 50, 50, 25, 25, 25, 25, 10, 10, 10, 10, 5, 5, 5, 5]
armourweights10 = [40, 40, 40, 40, 30, 30, 30, 30, 15, 15, 15, 15, 10, 10, 10, 10]
armourweights15 = [30, 30, 30, 30, 30, 30, 30, 30, 20, 20, 20, 20, 15, 15, 15, 15]
armourweights20 = [20, 20, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25, 20, 20, 20, 20]
armourweights25 = [10, 10, 10, 10, 15, 15, 15, 15, 20, 20, 20, 20, 25, 25, 25, 25]

player_save_file = "data.json"

printing_text_large_spacing = '\n══════════════ • ══════════════ \n'
combat_spacing_text = '────── ◈ ──────'
ability_spacing_text = '··─··'
