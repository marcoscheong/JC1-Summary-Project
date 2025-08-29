# 2025-summary-project

## Members

- Marcos
- Jacob
- Savio
- Yufan
- Vince

# This is a J1 Summary Project
- It is a simple MUD game about ...

```mermaid
classDiagram

    Maze : - rooms
    Maze : - starting_room
    Maze : - current_room

    Room : - id
    Room : - connects
    Room <|-- TreasureRoom
    Room <|-- MonsterRoom

    TreasureRoom : - currency
    MonsterRoom : - monster
    MonsterRoom : - availableMonsters

    Character : - stats
    Character : - ability
    Character : - inventory
    Character <|-- Player
    Character <|-- Monster
    Player : - inventory
    Monster : - stats

    Stats : - maxHealth
    Stats : - attack
    Stats : - currentHealth

    Game : - game_state
    Game : - maze
    Game : - storage
    Game : - player

    Choice : - topic
    Choice : - details

    CombatSequence : - base_elixer
    CombatSequence : - current_turn
    CombatSequence : - max_turns
    CombatSequence : - player
    CombatSequence : - monster
    CombatSequence : - saved_p
    CombatSequence : - saved_m

    Inventory : - storage
    Inventory : - file

    Ability : - name
    Ability : - attack
    Ability : - shield
    Ability : - heal
    Ability : - elixer
    Ability : - saved_elixer
    Ability : - magnitude

    class Room {
        + connection()
    }
    class Maze {
        + generate_maze()
        + get_room_key()
        + draw_rooms()
        + room_options()
        + travel_to()
    }
    class Game {
        + get_data()
        + get_options()
        + get_actions()
        + execute()
        + set_state()
        + get_state()
        + get_maze()
        + prompt_player_choice()
        + start_game()
        + quit_game()
        + welcome()
        + create_player()
        + get_player()
        + load_data()
        + store_currentdata()
    }
    class TreasureRoom {
        + generateItems()
    }
    class MonsterRoom {
        + generateMonster()
    }
    class Stats {
        + takeDamage()
        + heal()
    }
    class CombatSequence {
        + startSequence()
        + player_ability_sequence()
        + monster_ability_sequence()
        + endSequence()

    }
    class Storage {
        + get_data()
        + save_data()
    }

    class Player {
        + load_from_storage()
        + save_to_storage()
    }

    class Inventory {
        + add_item()
        + use_item()
        + remove_item()
        + save_inventory()
        + show_inventory()

    }