# 2025-summary-project

## Members

- Marcos
- Jacob
- Savio
- Yufan
- Vince

# This is a J1 Summary Project
- It is a simple MUD game about ...

classDiagram
    %% --- Core Game Controller ---
    class Game {
        -game_state: string
        -maze: Maze
        -storage: Storage
        -player: Player
        +set_state(state)
        +get_state()
        +get_maze()
        +get_options()
        +prompt_player_choice(choices)
        +start_game()
        +load_game()
        +pretty_print(text)
        +quit_game()
        +welcome()
        +create_player()
        +load_player()
        +get_player()
        +save_all_data(file)
    }

    class Storage {
        +get_data(file) dict
        +save_data(file, obj) None
    }

    %% --- World and Maze Structure ---
    class Maze {
        -rooms: list~Room~
        -starting_room: Room
        -current_room: Room
        +generate_maze()
        +get_room_key(room)
        +draw_rooms()
        +room_options()
        +travel_to(direction)
    }

    class Room {
        -id: int
        -connects: dict
        +connection(room, direction)
    }
    class TreasureRoom {
        -claimed: bool
        -drop: Drop
        +get_drops()
        +get_type()
    }
    class MonsterRoom {
        -claimed: bool
        -monster: string
        -availableMonsters: list
        -drop: Drop
        +generateMonster()
        +generateDrops()
    }
    class BossRoom {
        -claimed: bool
        -boss_monster_name: string
        -boss_monster: Monster
    }

    %% --- Characters and Stats ---
    class Character {
        -stats: Stats
        -abilities: list~Ability~
    }

    class Player {
        -inventory: Inventory
        -base_atk: int
        -base_health: int
        +create_new_storage(storage, file)
        +load_from_storage(storage, file)
        +save_to_storage(storage, file)
        +show_inventory()
        +recalculate_stats()
    }

    class Monster {
        %% Inherits attributes from Character
    }

    class Stats {
        -max_health: int
        -attack: int
        -current_health: int
        +take_damage(damage)
        +heal(healAmount)
        +return_stats() string
    }

    %% --- Items and Inventory ---
    class Inventory {
        -storage: Storage
        -file: string
        -items: dict
        +add_item(item_name, quantity)
        +use_item(item_name, quantity)
        +equip_weapon(weapon_name)
        +equip_armour(slot, armour_name)
        +remove_item(item_name)
        +save_inventory()
        +return_inventory() string
    }

    class Drop {
        -weaponWeights: list
        -armourWeights: list
        -name: string
        -type: string
        -drop: string
        +generateDrop()
        +generateArmourDrop()
        +generateWeaponDrop()
    }

    %% --- Combat System ---
    class CombatSequence {
        -base_elixir: int
        -current_turn: int
        -max_turns: int
        -player: Player
        -monster: Monster
        -saved_p: int
        -saved_m: int
        +start_sequence(is_boss)
        +start_boss_sequence()
        +player_ability_sequence(elixir)
        +monster_ability_sequence(elixir)
        +returnMonsterDrop()
        +end_sequence()
    }

    class Ability {
        -name: string
        -attack: int
        -shield: int
        -heal: int
        -elixir: int
        -saved_elixir: int
        -magnitude: int
    }

    %% --- Relationships ---
    Game "1" o-- "1" Maze
    Game "1" o-- "1" Player
    Game "1" o-- "1" Storage
    Maze "1" *-- "many" Room
    Room <|-- TreasureRoom
    Room <|-- MonsterRoom
    Room <|-- BossRoom
    TreasureRoom "1" -- "1" Drop
    MonsterRoom "1" -- "1" Drop

    Character <|-- Player
    Character <|-- Monster
    Character "1" o-- "1" Stats
    Player "1" o-- "1" Inventory

    CombatSequence "1" -- "1" Player
    CombatSequence "1" -- "1" Monster
