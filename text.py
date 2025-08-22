room_types = ['treasure', 'monster']

maze_size = 15

welcome_prompt = "Welcome to Labyrinth Ascension, a Single Player MUD game. Do you want to start or load your game?"
start_choices = ['start', 'quit', 'load']
started_text = 'To choose an option, type out the entire option.'

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
    |
    |
╭───────╮
│   -   │
│       │
╰───────╯
""",
    "S": """
╭───────╮
│   -   │
│       │
╰───────╯
    |
    |
""",
    "E": """
╭───────╮
│   -   ├──
│       │
╰───────╯
""",
    "W": """
  ╭───────╮
──┤   -   │
  │       │
  ╰───────╯
""",
    "NS": """
    |
    |
╭───────╮
│   -   │
│       │
╰───────╯
    |
    |
""",
    "NE": """
    |
    |
╭───────╮
│   -   ├──
│       │
╰───────╯
""",
    "NW": """
      |
      |
  ╭───────╮
──┤   -   │
  │       │
  ╰───────╯
""",
    "SE": """
╭───────╮
│   -   ├──
│       │
╰───────╯
    |
    |
""",
    "SW": """
  ╭───────╮
──┤   -   │
  │       │
  ╰───────╯
      |
      |
""",
    "EW": """
  ╭───────╮
──┤   -   ├──
  │       │
  ╰───────╯
""",
    "NSE": """
    |
    |
╭───────╮
│   -   ├──
│       │
╰───────╯
    |
    |
""",
    "NSW": """
      |
      |
  ╭───────╮
──┤   -   │
  │       │
  ╰───────╯
      |
      |
""",
    "NEW": """
      |
      |
  ╭───────╮
──┤   -   ├──
  │       │
  ╰───────╯
""",
    "SEW": """
  ╭───────╮
──┤   -   ├──
  │       │
  ╰───────╯
      |
      |
""",
    "NSEW": """      
      |
      |
  ╭───────╮
──┤   -   ├──
  │       │
  ╰───────╯
      |
      |
"""
}

player_rooms = {
    "N": """
    |
    |
╭───────╮
│   O   │
│       │
╰───────╯
""",
    "S": """
╭───────╮
│   O   │
│       │
╰───────╯
    |
    |
""",
    "E": """
╭───────╮
│   O   ├──
│       │
╰───────╯
""",
    "W": """
  ╭───────╮
──┤   O   │
  │       │
  ╰───────╯
""",
    "NS": """
    |
    |
╭───────╮
│   O   │
│       │
╰───────╯
    |
    |
""",
    "NE": """
    |
    |
╭───────╮
│   O   ├──
│       │
╰───────╯
""",
    "NW": """
      |
      |
  ╭───────╮
──┤   O   │
  │       │
  ╰───────╯
""",
    "SE": """
╭───────╮
│   O   ├──
│       │
╰───────╯
    |
    |
""",
    "SW": """
  ╭───────╮
──┤   O   │
  │       │
  ╰───────╯
      |
      |
""",
    "EW": """
  ╭───────╮
──┤   O   ├──
  │       │
  ╰───────╯
""",
    "NSE": """
    |
    |
╭───────╮
│   O   ├──
│       │
╰───────╯
    |
    |
""",
    "NSW": """
      |
      |
  ╭───────╮
──┤   O   │
  │       │
  ╰───────╯
      |
      |
""",
    "NEW": """
      |
      |
  ╭───────╮
──┤   O   ├──
  │       │
  ╰───────╯
""",
    "SEW": """
  ╭───────╮
──┤   O   ├──
  │       │
  ╰───────╯
      |
      |
""",
    "NSEW": """
      |
      |
  ╭───────╮
──┤   O   ├──
  │       │
  ╰───────╯
      |
      |
"""
}
