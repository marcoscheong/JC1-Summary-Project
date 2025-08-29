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

player_save_file = "player_data.json"

welcome_prompt = "Welcome to Labyrinth Ascension, a Single Player MUD game. Do you want to start or load your game?"
start_choices = ['start', 'load', 'quit', 'how to play']
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



default_health = 10
default_attack = 10

Monsters = {
    "Slime": [5, 1],
    "Pig": [8, 2],
    "Goblin": [12, 3],
    "Wolf": [20, 5],
    "Orc": [35, 8],
    "Skeleton": [50, 10],
    "Zombie": [70, 12],
    "Bandit": [90, 15],
    "Giant Spider": [120, 18],
    "Dark Knight": [180, 25],
    "Stone Golem": [180, 35],
    "Troll": [180, 40],
    "Wyvern": [250, 60],
    "Minotaur": [250, 70],
    "Hydra": [500, 90],
    "Ancient Treant": [200, 100],
    "Fire Drake": [450, 160],
    "Shadow Reaper": [50, 500],
    "Frost Titan": [1000, 20],
    "Chaos Serpent": [650, 280]
}


Weapon = {
    "Fist": 1,
    "Wooden Sword": 7,
    "Beginner Daggers": 7,
    "Beginner Wand": 7,
    "Stone Sword": 10,
    "Intermediate Daggers": 15,
    "Intermediate Wand": 15,
    "Iron Sword": 20,
    "Steel Sword": 35,
    "Knucklebuster": 55,
    "Silver Sword": 70,
    "Diamond Sword": 100,
    "Mythril Sword": 125,
    "Draconic Blade": 150,
    "Excalibur": 250
}

Consumable = {
  "health potion": 5,
  "attack potion": 5,
  "healing potion": 10
}
Armour = {
    "Leather Boots": 8, "Leather Leggings": 10, "Leather Helmet": 8, "Leather Chestplate": 16,
    "Chainmail Boots": 16, "Chainmail Leggings": 20, "Chainmail Helmet": 16, "Chainmail Chestplate": 32,
    "Iron Boots": 32, "Iron Leggings": 40, "Iron Helmet": 32, "Iron Chestplate": 64,
    "Diamond Boots": 64, "Diamond Leggings": 80, "Diamond Helmet": 64, "Diamond Chestplate": 128,
    "Draconic Boots": 128, "Draconic Leggings": 160, "Draconic Helmet": 128, "Draconic Chestplate": 256
}



ArmourSlots = {
    # Leather
    "Leather Helmet": "Helmet",
    "Leather Chestplate": "Chestplate",
    "Leather Leggings": "Leggings",
    "Leather Boots": "Boots",

    # Chainmail
    "Chainmail Helmet": "Helmet",
    "Chainmail Chestplate": "Chestplate",
    "Chainmail Leggings": "Leggings",
    "Chainmail Boots": "Boots",

    # Iron
    "Iron Helmet": "Helmet",
    "Iron Chestplate": "Chestplate",
    "Iron Leggings": "Leggings",
    "Iron Boots": "Boots",

    # Diamond
    "Diamond Helmet": "Helmet",
    "Diamond Chestplate": "Chestplate",
    "Diamond Leggings": "Leggings",
    "Diamond Boots": "Boots",

    # Draconic
    "Draconic Helmet": "Helmet",
    "Draconic Chestplate": "Chestplate",
    "Draconic Leggings": "Leggings",
    "Draconic Boots": "Boots",
}


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
boss_monster_stats = [2500, 250]

player_save_file = "player_data.json"
default_save_file = "data.json"

victory_text = "You have defeated the monster!"
defeat_text = "You have been defeated by the monster..."

printing_text_large_spacing = '\n══════════════ • ══════════════ \n'
combat_spacing_text = '────── ◈ ──────'
ability_spacing_text = '··─··'
equip_spacing_text = "───┈───"
