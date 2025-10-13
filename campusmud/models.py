# Data models - pure data classes for game stats and drops

import random
from typing import List

from campusmud.data import load_game_data

game_data = load_game_data()
Consumable = game_data["items"]["consumables"]
Armour = game_data["items"]["armor"]
Weapon = game_data["items"]["weapons"]


def create_consumable(name: str) -> "Potion":
    """Create a consumable item by name."""
    if name not in game_data["items"]["consumables"]:
        raise ValueError(f"Consumable '{name}' not found.")
    bonus = game_data["items"]["consumables"][name]["bonus"]
    if name == "health potion":
        return HealthPotion(name, bonus)
    elif name == "attack potion":
        return AttackPotion(name, bonus)
    elif name == "healing potion":
        return HealingPotion(name, bonus)
    else:
        raise ValueError(f"Unknown consumable type: {name}")


def create_armor(name: str) -> "Armor":
    """Create an armor item by name."""
    if name not in game_data["items"]["armor"]:
        raise ValueError(f"Armor '{name}' not found.")
    defense_bonus = game_data["items"]["armor"][name]["defense_bonus"]
    return Armor(name, defense_bonus)


def create_weapon(name: str) -> "Weapon":
    """Create a weapon item by name."""
    if name not in game_data["items"]["weapons"]:
        raise ValueError(f"Weapon '{name}' not found.")
    attack_bonus = game_data["items"]["weapons"][name]["attack_bonus"]
    return Weapon(name, attack_bonus)


class Item:
    """Base class for items."""

    def __init__(self, name: str) -> None:
        self.name: str = name


class Potion(Item):
    """Represents a consumable potion item.
    
    Potions provide a bonus effect to one or more attributes.
    """

    def __init__(self, name: str, bonus: int) -> None:
        super().__init__(name)
        self.bonus: int = bonus


class HealthPotion(Potion):
    """Represents a health potion that restores health."""


class AttackPotion(Potion):
    """Represents an attack potion that boosts attack power."""


class HealingPotion(Potion):
    """Represents a healing potion that heals over time."""


class Armor(Item):
    """Represents an armor item that provides a defense bonus."""

    def __init__(self, name: str, defense_bonus: int) -> None:
        super().__init__(name)
        self.defense_bonus: int = defense_bonus


class WeaponItem(Item):
    """Represents a weapon item that provides an attack bonus."""

    def __init__(self, name: str, attack_bonus: int) -> None:
        super().__init__(name)
        self.attack_bonus: int = attack_bonus


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
            drop = random.choices(list(Weapon.keys()), self.weaponWeights)[0]
            self.type: str = 'weapon'
        elif r == 1:
            drop = random.choices(list(Armour.keys()), self.armourWeights)[0]
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
        drop: str = random.choices(list(Armour.keys()), self.armourWeights)[0]
        self.type: str = 'armour'
        self.drop = drop
        return self
        
    def generateWeaponDrop(self) -> 'Drop':
        """
        Generate only a weapon drop.
        """
        drop: str = random.choices(list(Weapon.keys()), self.weaponWeights)[0]
        self.type: str = 'weapon'
        self.drop = drop
        return self


class Ability:
    """Represents a player action during combat (attack, shield, heal, save)."""
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.attack: int = 0
        self.shield: int = 0
        self.heal: int = 0
        self.elixir: int = 1
        self.saved_elixir: int = 0
        self.magnitude: int = 0
