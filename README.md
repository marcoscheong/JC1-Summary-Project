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
    Maze <|-- Room
    Maze : - rooms
    Maze : - starting_room
    Maze : - str_chain
    Room : - id
    Room : - connect
    class Room{
        + Connection()
    }
    class Maze{
        + generate_maze()
        + draw_rooms()
    }

```