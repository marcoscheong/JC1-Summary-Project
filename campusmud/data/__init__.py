import json
import os

def load_game_data():
    """Load game data from gamedata.json."""
    file_path = os.path.join(os.path.dirname(__file__), 'gamedata.json')
    with open(file_path, 'r') as file:
        return json.load(file)
