# Maze module - Room classes and Maze generation/navigation

import random
from typing import Optional, Dict, List

from labyrinth import config, entities, text
from labyrinth.entities import Monster


def generate_monster(
        level: int,
        available_monsters: List[str] = entities.MONSTERS
) -> Monster:
    """Generate a random monster based on room ID (difficulty).
    Higher ID increases chance of stronger monsters.
    """
    if not available_monsters:
        raise ValueError("available_monsters cannot be empty.")

    # Determine max index based on player progress
    max_index: int = min(len(available_monsters) - 1, level // 2)

    # Randomly pick a monster from the range [0, max_index]
    monster_name = available_monsters[random.randint(0, max_index)]
    return entities.create_monster(monster_name)


def generate_room(id: int) -> "Room":
    """Generate a basic room."""
    if id == 0:
        return Room(0)
    elif id == -1:
        return BossRoom(config.MAZE_SIZE + 1)
    elif id % 2 == 0:
        level = id + 1
        return MonsterRoom(id=level, monster=generate_monster(level))
    else:
        level = id + 1
        return TreasureRoom(
            id=level,
            treasure_type=random.choice(["weapon", "armor"])
        )


def generate_maze() -> "Maze":
    """Generate a maze with rooms and a boss room at the end."""
    rooms: list[Room] = [
        generate_room(i) for i in range(config.MAZE_SIZE + 1)
    ]
    maze = Maze(rooms)
    maze.connect_rooms()
    return maze


class Room:
    """Basic room with connections to other rooms."""

    def __init__(self, id: int) -> None:
        self.id: int = id
        self.connections: Dict[str, Optional[Room]] = {
            "up": None,
            "left": None,
            "right": None,
            "down": None
        }

    def connect(self, room: 'Room', direction: str) -> None:
        """Connect this room to another room in a given direction."""
        if direction in self.connections:
            self.connections[direction] = room

    def get_boss_direction(self) -> Optional[str]:
        """Return the direction leading to the boss room, if connected."""
        for direction, room in self.connections.items():
            if isinstance(room, BossRoom):
                return direction
        return None

    def get_room(self, direction: str) -> Optional['Room']:
        """Return the room connected in the given direction, if any."""
        return self.connections[direction]

    def get_options(self) -> list[str]:
        """Return list of available movement options based on room connections."""
        options: List[str] = []
        for direction, room in self.connections.items():
            if room is not None:
                # Special handling for boss room access
                options.append(
                    'enter boss chamber' if isinstance(room, BossRoom)
                    else 'Go ' + direction
                )
        return options

    def to_dict(self) -> dict:
        """Return a dictionary representation of the room."""
        return {
            "id": self.id,
        }

class CompletableRoom(Room):
    """Room that can be completed (e.g., treasure or monster room)."""

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.completed: bool = False

    def complete(self) -> None:
        """Mark the room as completed."""
        self.completed = True

    def to_dict(self) -> dict:
        """Return a dictionary representation of the completable room."""
        base_dict = super().to_dict()
        base_dict.update({"completed": self.completed})
        return base_dict


class TreasureRoom(CompletableRoom):
    """Room containing treasure drops."""

    def __init__(self, id: int, treasure_type: str) -> None:
        """Initialize room with treasure based on room ID (difficulty)."""
        super().__init__(id)
        self.treasure_type: str = treasure_type  # 'weapon', 'armor', or 'consumable'

    def get_options(self) -> list[str]:
        options = super().get_options()
        if not self.completed:
            options.append('Open chest')
        return options

    def get_type(self):
        """Return the type of item in the treasure room."""
        return self.treasure_type

    def to_dict(self) -> dict:
        """Return a dictionary representation of the treasure room."""
        base_dict = super().to_dict()
        base_dict.update({"treasure_type": self.treasure_type})
        return base_dict


class MonsterRoom(CompletableRoom):
    """Room containing monsters to fight."""

    def __init__(self, id: int, monster: entities.Monster) -> None:
        """Initialize room with monster generation settings."""
        super().__init__(id)
        self.monster = monster

    def get_options(self) -> list[str]:
        options = super().get_options()
        if not self.completed:
            options.append('Fight monster')
        return options

    def to_dict(self) -> dict:
        """Return a dictionary representation of the monster room."""
        base_dict = super().to_dict()
        base_dict.update(
            {"monster": self.monster.name if self.monster else None}
        )
        return base_dict


class BossRoom(MonsterRoom):
    """Final boss room."""

    def __init__(self, id: int) -> None:
        super().__init__(id, entities.create_boss())

    def get_options(self) -> list[str]:
        options = super().get_options()
        if not self.completed:
            options.append('Challenge the boss')
        return options


class Maze:
    """Grid-based maze with rooms connected by directions."""

    def __init__(self, rooms: List[Room], cols: int = config.MAZE_COLS) -> None:
        """Create a maze from a list of Room objects."""
        self.rooms = rooms
        self.starting_room = rooms[0]
        self.col_count = cols
        # Exclude boss room from row count
        self.row_count = divmod(len(rooms) - 1, cols)[0] + 1

    def get(self, x: int, y: int) -> Optional[Room]:
        """Get room at grid coordinates (x, y)."""
        if not (0 <= x < self.col_count and 0 <= y < self.row_count):
            return None
        index = y * self.col_count + x
        return self.rooms[index]
    
    def get_boss_room(self) -> BossRoom:
        """Return the boss room."""
        boss_room = self.rooms[-1]  # Assuming last room is always the boss room
        assert isinstance(boss_room, BossRoom), "Last room is not a BossRoom."
        return boss_room

    def get_start_room(self) -> Room:
        """Return the starting room."""
        return self.starting_room

    def connect_rooms(self) -> None:
        """
        Generate a col_count-column grid maze connecting all rooms.
        The last room is the boss room connected to the bottom.
        """
        regular_rooms = self.rooms[:-1]
        assert regular_rooms, "Maze must have at least one regular room."
        for i, room in enumerate(regular_rooms):
            row, col = divmod(i, self.col_count)
            room = self.get(col, row)
            left_room = self.get(col - 1, row)
            right_room = self.get(col + 1, row)
            up_room = self.get(col, row - 1)
            down_room = self.get(col, row + 1)
            if left_room is not None:
                room.connect(left_room, 'left')
            if right_room is not None:
                room.connect(right_room, 'right')
            if up_room is not None:
                room.connect(up_room, 'up')
            if down_room is not None:
                room.connect(down_room, 'down')

        # Connect boss room to last regular room
        boss_room = self.get_boss_room()
        room.connect(boss_room, 'down')
        boss_room.connect(room, 'up')

    def get_room_key(self, room: Room) -> str:
        """
        Return a string key representing room connections for display.
        N=North/up, S=South/down, E=East/right, W=West/left.
        """
        # Convert room objects to boolean values
        up: bool = room.connections['up'] is not None
        down: bool = room.connections['down'] is not None
        left: bool = room.connections['left'] is not None
        right: bool = room.connections['right'] is not None

        if isinstance(room, BossRoom):
            return "BOSS_CLEAN"
        
        key = ""
        if up:
            key += "N"
        if down:
            key += "S"
        if left:
            key += "W"
        if right:
            key += "E"
        return key

    def draw_rooms(self, current_room: Room) -> None:
        """Display the maze layout as ASCII art showing all rooms in a grid."""
        row_chunks: List[List[str]] = []
        rooms_per_row: int = 3
        
        regular_rooms: List[Room] = self.rooms[:-1]  # Exclude boss room
        
        # Draw regular rooms in grid
        for row_start in range(0, len(regular_rooms), rooms_per_row):
            row_rooms: List[Room] = regular_rooms[row_start:row_start + rooms_per_row]
            
            row_arts: List[str] = []
            for room in row_rooms:
                if room.id == current_room.id:
                    room_art: str = text.player_rooms[self.get_room_key(room)]
                else:
                    room_art: str = text.rooms[self.get_room_key(room)]
                row_arts.append(room_art)
            
            if not row_arts:
                continue
                
            max_height: int = max(len(art.strip("\n").splitlines()) for art in row_arts)
            max_width: int = max(max(len(line) for line in art.strip("\n").splitlines()) for art in row_arts)
            
            row_chunk: List[List[str]] = [[] for _ in range(max_height)]
            
            for art in row_arts:
                lines: List[str] = art.strip("\n").splitlines()
                lines = [line.ljust(max_width) for line in lines]
                
                while len(lines) < max_height:
                    lines.append(" " * max_width)
                
                for i, line in enumerate(lines):
                    row_chunk[i].append(line)
            
            row_chunks.append(row_chunk)
        
        # Print regular maze
        map_str: str = ""
        for row in row_chunks:
            for line in row:
                map_str += "".join(line) + "\n"
        
        print(map_str.rstrip("\n"))
        
        # Print boss area separately
        boss_room: Room = self.rooms[-1]
        print("=" * 15)
        if boss_room.id == current_room.id:
            print("BOSS CHAMBER (YOU ARE HERE)")
        else:
            print("BOSS CHAMBER")
        print("=" * 15)
        
        if boss_room.id == current_room.id:
            boss_art: str = text.player_rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        else:
            boss_art: str = text.rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        
        boss_lines: List[str] = boss_art.strip("\n").splitlines()
        for line in boss_lines:
            print(line.center(14) + '\n')

    def to_dict(self) -> dict:
        """Return a dictionary representation of the maze."""
        return {
            "rooms": [room.to_dict() for room in self.rooms],
            "current_room_id": self.current_room.id,
            "col_count": self.col_count,
            "row_count": self.row_count
        }
