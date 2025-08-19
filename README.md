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
    Character : - inventory
    Character <|-- Player
    Character <|-- Monster
    Player : - inventory
    Monster: - stats


    Stats : - maxHealth
    Stats : - attack
    Stats : - currentHealth

    Game : - game_state
    Game : - maze

    Choice : - topic
    Choice : - details


    CombatSequence : - points
    class Room{
        + Connection()
    }
    class Maze{
        + generate_maze()
        + draw_rooms()
        + room_options()
        + travel_to()
    }
    class Game{
        + get_data()
        + get_options()
        + get_actions()
        + execute()
    }
    class TreasureRoom{
        + generateItems()
    }

    class MonsterRoom{
        + generateMonster()
    }
    
    class Stats{
        + takeDamage()
        + heal()
    }
    
    class CombatSequence{
        + startSequence()
        + endSequence()
    }

    class Storage{
        + get_data()
        + save_data()

    class Room{
        + connections()
    }
    }
```