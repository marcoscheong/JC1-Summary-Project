Game_name = "Gametitle": "Labyrinth Ascension"
Game_info = "Game_info": [
    "Explore Maze Rooms: Each maze run is procedurally generated (different layouts each time).",
    "Rooms contain enemies, puzzles, traps, or treasure.",
    "Fight Enemies: Defeat enemies to gain EXP and Rank Points.",
    "Enemies drop loot (weapons, health, buffs).",
    "Level Up & Rank Up: EXP increases your Level (boosts stats like health, speed, attack).",
    "Rank Points increase your Rank Tier (unlocks new abilities).",
    "Progressive Difficulty: Higher ranks unlock deeper maze layers with harder enemies and better rewards.",
    "Death & Respawn: If you die, you respawn at your base camp with your rank intact but lose temporary loot."
  ]

Game_lore = "Game_lore": [
    "In a world where warriors prove themselves in an endless shifting labyrinth, your journey starts at rock bottom.",
    "Climb the ranks, earn your place among legends, and uncover the secret of the maze — a truth that might change everything."
  ]
room_types = ['treasure', 'monster']
action_states = {
    'travel': 'travelling', 
    'fight': 'fighting'}
input_prompt = "Please select a choice: "
input_error_prompt = "Please input a valid option"
successful_room_travel = "You have travelled to room with ID: "
thanks_message = "Thanks for playing!"
directions = ['up', 'down', 'left', 'right']