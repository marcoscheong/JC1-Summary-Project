# Maze module - Room classes and Maze generation/navigation

import random
from typing import Optional, Dict, List

from campusmud import text
from campusmud.data import load_game_data
from campusmud.models import Drop
from campusmud.entities import Monster

BOSS_NAME = "Origin of Chaos"

game_data = load_game_data()

Monsters = {
    name: [data["max_health"], data["attack"]]
    for name, data in game_data["monsters"].items()
}


class Room:
    """Basic room with connections to other rooms."""

    def __init__(self, id: int) -> None:
        self.id: int = id
        self.connects: Dict[str, Optional[Room]] = {'up': None, 'left': None, 'right': None, 'down': None}

    def connection(self, room: 'Room', direction: str) -> None:
        """Connect this room to another room in a given direction."""
        if direction in self.connects:
            self.connects[direction] = room


class TreasureRoom(Room):
    """
    Room containing treasure drops.
    """
    def __init__(self, _id: int, treasure_type: str) -> None:
        """Initialize room with treasure based on room ID (difficulty)."""
        super().__init__(_id)
        self.treasure_type: str = treasure_type  # 'weapon', 'armor', or 'consumable'
        self.claimed: bool = False

    def get_type(self):
        """Return the type of item in the treasure room."""
        return self.treasure_type


class MonsterRoom(Room):
    """
    Room containing monsters to fight.
    """
    def __init__(self, id: int, availableMonsters: List[str]) -> None:
        """Initialize room with monster generation settings."""
        super().__init__(id)
        self.monster: str = ''
        # Convert dict_keys view to list to avoid issues
        self.availableMonsters: List[str] = list(availableMonsters)
        self.claimed: bool = False

    def generateMonster(self) -> None:
        """Generate a random monster based on room ID (difficulty).
        Higher ID increases chance of stronger monsters.
        """
        if len(self.availableMonsters) == 0:
            return

        # Determine max index based on player progress
        max_index: int = min(len(self.availableMonsters) - 1, self.id // 2)

        # Randomly pick a monster from the range [0, max_index]
        self.monster = self.availableMonsters[random.randint(0, max_index)]

    def generateDrops(self) -> None:
        """Generate drops that the monster will drop when defeated."""
        i: int = random.randint(0, 1)
        if i == 0:
            if self.id < 5:
                drop = Drop(text.weaponweights5, text.armourweights5)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 10:
                drop = Drop(text.weaponweights10, text.armourweights10)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 15:
                drop = Drop(text.weaponweights15, text.armourweights15)
                drop.generateArmourDrop()
                self.drop = drop
            elif self.id < 20: 
                drop = Drop(text.weaponweights20, text.armourweights20)
                drop.generateArmourDrop()
                self.drop = drop
            else:
                drop = Drop(text.weaponweights25, text.armourweights25)
                drop.generateArmourDrop()
                self.drop = drop
        elif i == 1:
            if self.id < 5:
                drop = Drop(text.weaponweights5, text.armourweights5)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 10:
                drop = Drop(text.weaponweights10, text.armourweights10)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 15:
                drop = Drop(text.weaponweights15, text.armourweights15)
                drop.generateWeaponDrop()
                self.drop = drop
            elif self.id < 20: 
                drop = Drop(text.weaponweights20, text.armourweights20)
                drop.generateWeaponDrop()
                self.drop = drop
            else:
                drop = Drop(text.weaponweights25, text.armourweights25)
                drop.generateWeaponDrop()
                self.drop = drop


class BossRoom(Room):
    """
    Final boss room.
    """
    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.claimed: bool = False
        self.boss_monster_name: str = BOSS_NAME
        self.boss_monster: Monster = Monster(Monsters[BOSS_NAME][0], Monsters[BOSS_NAME][1])


class Maze:
    """
    Grid-based maze with rooms connected by directions.
    """
    def __init__(self, rooms: List[Room], starting_room: Room) -> None:
        """
        Create a maze from a list of Room objects.
        """
        self.rooms: List[Room] = rooms
        self.starting_room: Room = starting_room
        self.current_room: Room = starting_room

    def generate_maze(self) -> None:
        """
        Generate a 3-column grid maze connecting all rooms.
        The last room is the boss room connected to the bottom.
        """
        num_cols: int = 3
        regular_rooms: List[Room] = self.rooms[:-1]
        
        for i, room in enumerate(regular_rooms):
            row: int = i // num_cols
            col: int = i % num_cols
            
            # Connect horizontally (left-right)
            if col < num_cols - 1 and (i + 1) < len(regular_rooms):
                right_room: Room = regular_rooms[i + 1]
                room.connection(right_room, 'right')
                right_room.connection(room, 'left')
            
            # Connect vertically (up-down)
            num_rows: int = (len(regular_rooms) + num_cols - 1) // num_cols
            if row < num_rows - 1 and (i + num_cols) < len(regular_rooms):
                down_room: Room = regular_rooms[i + num_cols]
                room.connection(down_room, 'down')
                down_room.connection(room, 'up')
        
        # Connect boss room to last regular room
        boss_room: Room = self.rooms[-1]
        last_regular_room: Room = regular_rooms[-1]
        boss_room.connection(last_regular_room, 'up')
        last_regular_room.connection(boss_room, 'down')

    def get_room_key(self, room: Room) -> str:
        """
        Return a string key representing room connections for display.
        N=North/up, S=South/down, E=East/right, W=West/left.
        """
        # Convert room objects to boolean values
        up: bool = room.connects['up'] is not None
        down: bool = room.connects['down'] is not None
        left: bool = room.connects['left'] is not None
        right: bool = room.connects['right'] is not None

        if isinstance(room, BossRoom):
            return "BOSS_CLEAN"

        if up and down and left and right: return "NSEW"

        if up and down and left and not right: return "NSW"
        if up and down and not left and right: return "NSE"
        if up and not down and left and right: return "NEW"
        if not up and down and left and right: return "SEW"

        if up and down and not left and not right: return "NS"
        if not up and not down and left and right: return "EW"
        if up and not down and left and not right: return "NW"
        if up and not down and not left and right: return "NE"
        if not up and down and left and not right: return "SW"
        if not up and down and not left and right: return "SE"

        if up and not down and not left and not right: return "N"
        if not up and down and not left and not right: return "S"
        if not up and not down and left and not right: return "W"
        if not up and not down and not left and right: return "E"
        return "BOSS"

    def draw_rooms(self) -> None:
        """
        Display the maze layout as ASCII art showing all rooms in a grid.
        """
        row_chunks: List[List[str]] = []
        rooms_per_row: int = 3
        
        regular_rooms: List[Room] = self.rooms[:-1]  # Exclude boss room
        
        # Draw regular rooms in grid
        for row_start in range(0, len(regular_rooms), rooms_per_row):
            row_rooms: List[Room] = regular_rooms[row_start:row_start + rooms_per_row]
            
            row_arts: List[str] = []
            for room in row_rooms:
                if room.id == self.current_room.id:
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
        if boss_room.id == self.current_room.id:
            print("BOSS CHAMBER (YOU ARE HERE)")
        else:
            print("BOSS CHAMBER")
        print("=" * 15)
        
        if boss_room.id == self.current_room.id:
            boss_art: str = text.player_rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        else:
            boss_art: str = text.rooms.get(self.get_room_key(boss_room), "[ BOSS ROOM ]")
        
        boss_lines: List[str] = boss_art.strip("\n").splitlines()
        for line in boss_lines:
            print(line.center(14) + '\n')
    
    def room_options(self) -> List[str]:
        """
        Return list of available movement options based on current room connections.
        """
        options: List[str] = []
        for direction in text.directions:
            connected_room: Optional[Room] = self.current_room.connects.get(direction)
            if connected_room:
                # Special handling for boss room access
                if isinstance(connected_room, BossRoom):
                    options.append('enter boss chamber')
                else:
                    options.append('Go ' + direction)
        return options

    def travel_to(self, direction: str) -> None:
        """
        Move player to an adjacent room in the given direction.
        """
        # Handle special boss room access
        if direction == 'boss chamber' or direction == 'boss':
            # Find if current room connects to boss room
            for dir_key, connected_room in self.current_room.connects.items():
                if isinstance(connected_room, BossRoom):
                    self.current_room = connected_room
                    print("You step through the ominous doorway into the Boss Chamber...")
                    return
            print("You cannot access the Boss Chamber from here.")
            return
        
        # Regular movement
        connected_room: Optional[Room] = self.current_room.connects.get(direction)
        if connected_room:
            self.current_room = connected_room
            if isinstance(connected_room, BossRoom):
                print("You enter the foreboding Boss Chamber...")
            else:
                print(text.successful_room_travel + str(connected_room.id))
