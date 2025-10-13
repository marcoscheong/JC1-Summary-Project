"""Configuration constants for Campus MUD game."""

# Game configuration
from labyrinth.data import load_game_data


MAZE_SIZE: int = 5
DEFAULT_HEALTH: int = 100
DEFAULT_ATTACK: int = 10

# Save file names
DEFAULT_SAVE_FILE: str = 'data.json'
PLAYER_SAVE_FILE: str = 'player_data.json'

# Combat constants
DEFAULT_BOSS_HEALTH_MULTIPLIER: int = 3
DEFAULT_BOSS_ATTACK_MULTIPLIER: int = 2

_game_data = load_game_data()
WEIGHTS = _game_data["weights"]