# Data models - pure data classes for game stats and drops

import random
from typing import List

from campusmud import text


class Drop:
    """
    Represents loot dropped from monsters (weapon, armour, or consumable).
    """
    def __init__(self, weaponWeights: List[int], armourWeights: List[int]) -> None:
        self.weaponWeights: List[int] = weaponWeights
        self.armourWeights: List[int] = armourWeights
        self.name: str = ''
    
    def generateDrop(self) -> 'Drop':
        """
        Randomly generate a weapon, armour, or consumable drop.
        """
        r: int = random.randint(0, 2)
        drop: str = ''  # Initialize variable to avoid unbound error
        if r == 0:
            drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
            self.type: str = 'weapon'
        elif r == 1:
            drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
            self.type = 'armour'
        elif r == 2:
            number: int = random.randint(1, 3)
            if number == 1:
                drop = 'attack potion'
                self.type = 'consumable'
            elif number == 2:
                drop = 'health potion'
                self.type = 'consumable'
            else:
                drop = 'healing potion'
                self.type = 'consumable'
        self.drop: str = drop
        return self
    
    def generateArmourDrop(self) -> 'Drop':
        """
        Generate only an armour drop.
        """
        drop: str = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
        self.type: str = 'armour'
        self.drop = drop
        return self
        
    def generateWeaponDrop(self) -> 'Drop':
        """
        Generate only a weapon drop.
        """
        drop: str = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
        self.type: str = 'weapon'
        self.drop = drop
        return self


class Ability:
    """
    Represents a player action during combat (attack, shield, heal, save).
    """
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.attack: int = 0
        self.shield: int = 0
        self.heal: int = 0
        self.elixir: int = 1
        self.saved_elixir: int = 0
        self.magnitude: int = 0
