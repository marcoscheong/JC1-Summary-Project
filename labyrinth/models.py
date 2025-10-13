# Data models - pure data classes for game stats and drops

from labyrinth.data import load_game_data

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
    armor_type = game_data["items"]["armor"][name]["type"]
    defense_bonus = game_data["items"]["armor"][name]["defense_bonus"]
    if armor_type == "boots":
        return Boots(name, defense_bonus)
    elif armor_type == "chestplate":
        return Chestplate(name, defense_bonus)
    elif armor_type == "helmet":
        return Helmet(name, defense_bonus)
    elif armor_type == "leggings":
        return Leggings(name, defense_bonus)
    else:
        raise ValueError(f"Unknown armor type: {armor_type}")


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


class Boots(Armor):
    """Represents boots armor."""


class Chestplate(Armor):
    """Represents a chestplate armor."""


class Helmet(Armor):
    """Represents a helmet armor."""


class Leggings(Armor):
    """Represents leggings armor."""


class Weapon(Item):
    """Represents a weapon item that provides an attack bonus."""

    def __init__(self, name: str, attack_bonus: int) -> None:
        super().__init__(name)
        self.attack_bonus: int = attack_bonus
