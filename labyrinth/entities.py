# Entities - Character, Player, Monster, and Inventory classes

from typing import Optional

from labyrinth import config, models, text
from labyrinth.data import load_game_data
from labyrinth.storage import Storage

game_data = load_game_data()

# Constants
BOSS_NAME = "Origin of Chaos"

# Enums
MONSTERS = list(game_data["monsters"].keys())
MOVES = list(game_data["moves"])


def create_boss() -> "Monster":
    """Factory function to create the boss monster."""
    return create_monster(BOSS_NAME)

def create_monster(name: str) -> "Monster":
    """Factory function to create a Monster instance by name."""
    if name not in game_data["monsters"]:
        raise ValueError(f"Monster '{name}' not found in game data.")
    if name == BOSS_NAME:
        raise ValueError(
            f"Use create_boss() to create the boss monster '{BOSS_NAME}'."
        )
    monster_data = game_data["monsters"][name]
    return Monster(
        name=name,
        max_health=monster_data["max_health"],
        attack=monster_data["attack"]
    )

def create_player() -> "Player":
    """Factory function to create a Player instance with default stats."""
    return Player(
        name="Player",
        max_health=game_data["player"]["max_health"],
        attack=game_data["player"]["attack"],
    )


class Character:
    """
    Base class for all characters (player and monsters).
    """
    def __init__(self, name: str, max_health: int, attack: int) -> None:
        self.name: str = name
        self.max_health: int = max_health
        self.attack: int = attack
        self.current_health: int = max_health
        self.abilities = [
            name for name in MOVES
        ]

    def to_string(self) -> str:
        return f"{self.name} (ATK: {self.attack}, HP: {self.current_health}/{self.max_health})"

    def is_dead(self) -> bool:
        """Check if the character is dead."""
        return self.current_health <= 0

    def calculate_atk(self) -> int:
        """Calculate total attack including weapon bonus."""
        return self.attack

    def calculate_def(self) -> int:
        """Calculate total defense including armor bonus."""
        return 0

    def take_damage(self, damage: int) -> None:
        """Reduce health by damage amount."""
        self.current_health -= damage
        if self.current_health <= 0:
            self.current_health = 0

    def heal(self, healAmount: int | float) -> int:
        """Increase current health up to max_health.
        
        Returns the amount of health actually healed.
        """
        healAmount = round(healAmount)
        if self.current_health + healAmount > self.max_health:
            healAmount = self.max_health - self.current_health
            self.current_health = self.max_health
        else:
            self.current_health += healAmount
        return healAmount

    def strengthen(self, amt: int | float) -> int:
        """Increase the character's attack.
        
        Returns the amount of attack actually increased.
        """
        amt = round(amt)
        self.attack += amt
        return amt

    def return_stats(self) -> str:
        """Return a formatted string of the player's stats."""
        lines: list[str] = ["╔═ Player Stats ═════════════╗"]
        lines.append(f"  Health      » {self.current_health}/{self.max_health}")
        lines.append(f"  Attack      » {self.attack}")
        lines.append("╚═══════════════════════════╝")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the character."""
        return {
            "name": self.name,
            "max_health": self.max_health,
            "attack": self.attack,
            "current_health": self.current_health
        }


class Player(Character):
    """Player character with inventory and stat management."""

    def __init__(self,
                 name: str,
                 max_health: int,
                 attack: int,
                 base_atk: Optional[int] = None,
                 base_health: Optional[int] = None,
                 inventory: Optional[dict] = None,
                 weapon: Optional[str] = None,
                 armor: Optional[dict] = None) -> None:
        super().__init__(name, max_health, attack)
        self.base_atk: int = base_atk or attack
        self.base_health: int = base_health or max_health
        self.inventory = (
            Inventory.from_dict(inventory) if inventory
            else Inventory()
        )
        if armor:
            self.armor = {
                part: models.create_armor(armor[part]) if armor[part] else None
                for part in ["Helmet", "Chestplate", "Leggings", "Boots"]
            }
        else:
            self.armor: dict[str, Optional[models.Armor]] = {
                "Helmet": None,
                "Chestplate": None,
                "Leggings": None,
                "Boots": None
            }
        if weapon:
            self.weapon = models.create_weapon(weapon) if weapon else None

    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create a Player instance from a dictionary."""
        return cls(
            name=data["name"],
            max_health=data["max_health"],
            attack=data["attack"],
            base_atk=data.get("base_atk"),
            base_health=data.get("base_health"),
            inventory=data.get("inventory"),
            weapon=data.get("weapon"),
            armor=data.get("armor")
        )

    def calculate_atk(self) -> int:
        """Calculate total attack including weapon bonus."""
        if self.weapon:
            return self.base_atk + self.weapon.attack_bonus
        return self.base_atk

    def calculate_def(self) -> int:
        """Calculate total defense including armor bonus."""
        if self.armor:
            total_defence_bonus = sum(
                part.defence_bonus for part in self.armor.values()
                if part is not None
            )
            return total_defence_bonus
        return 0

    def equip(self, item: models.Item) -> bool:
        """Equip an item (weapon or armor)."""
        if isinstance(item, models.Weapon):
            return self.equip_weapon(item)
        elif isinstance(item, models.Armor):
            return self.equip_armor(item)
        else:
            print("Cannot equip this item type.")
            return False

    def equip_armor(self, armor: models.Armor) -> bool:
        """Equip armor to a specific slot."""
        if isinstance(armor, models.Helmet):
            self.armor["Helmet"] = armor
        elif isinstance(armor, models.Chestplate):
            self.armor["Chestplate"] = armor
        elif isinstance(armor, models.Leggings):
            self.armor["Leggings"] = armor
        elif isinstance(armor, models.Boots):
            self.armor["Boots"] = armor
        else:
            raise ValueError(f"Not armor: {armor}")
        return True

    def equip_weapon(self, weapon: models.Weapon) -> bool:
        self.weapon = weapon
        return True

    def show_inventory(self) -> None:
        """Display the player's inventory."""
        if self.inventory:
            print(self.inventory.to_string())
        else:
            print("No inventory loaded.")
    
    def atk_potion(self, amt: int) -> None:
        """Increase player's base attack."""
        self.base_atk += amt
    
    def health_potion(self, amt: int) -> None:
        """Increase player's base health."""
        self.base_health += amt

    def recalculate_stats(self) -> None:
        """Recalculate stats based on equipped items and base stats."""
        # Reset attack and health back to base
        self.attack = self.base_atk
        old_max_health = self.max_health
        old_current_health = self.current_health

        if self.inventory:
            weapon = self.inventory.items.get("Weapon", None)
            attack_bonus = text.Weapon.get(weapon, 0) if weapon else 0

            armour = self.inventory.items.get("Armour", {})
            defence_bonus = sum(text.Armour.get(part, 0) for part in armour.values() if part)

            self.attack = self.base_atk + attack_bonus
            self.max_health = self.base_health + defence_bonus

            if old_max_health > 0:
                health_ratio = old_current_health / old_max_health
            else:
                health_ratio = 1.0

            self.current_health = int(round(self.max_health * health_ratio))

            # Ensure it never goes above max
            if self.current_health > self.max_health:
                self.current_health = self.max_health

    def to_dict(self) -> dict:
        """Return a dictionary representation of the player."""
        base_dict = super().to_dict()
        base_dict.update({
            "inventory": self.inventory.to_dict() if self.inventory else {},
            "base_atk": self.base_atk,
            "base_health": self.base_health,
            "armor": {k: v.name if v else None for k, v in self.armor.items()},
            "weapon": self.weapon.name if self.weapon else None
        })
        return base_dict


class Monster(Character):
    """Monster character with basic stats."""
    

class Inventory:
    """Player inventory with weapons, armour, and consumables."""

    def __init__(self, items: Optional[dict[str, dict[str, int]]] = None) -> None:
        self.items: dict[str, dict[str, int]] = items or {
            "Weapon": {},
            "Armour": {},
            "Consumables": {}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Inventory':
        """Create an Inventory instance from a dictionary."""
        return cls(items=data)

    def _get_inventory(self, item_name: str) -> dict[str, int]:
        """Retrieve the correct inventory category for an item."""
        if item_name in models.CONSUMABLES:
            return self.items["Consumables"]
        elif item_name in models.WEAPONS:
            return self.items["Weapon"]
        elif item_name in models.ARMOR:
            return self.items["Armour"]
        else:
            raise ValueError(f"Unknown item: {item_name}")

    def add_item(self, item_name: str, quantity: int = 1) -> None:
        """Add an item to inventory."""
        inventory = self._get_inventory(item_name)
        # Put in inventory
        if item_name in inventory:
            inventory[item_name] += quantity
        else:
            inventory[item_name] = quantity

    def list_items(self) -> dict[str, int]:
        """List all items in inventory."""
        item_list: dict[str, int] = {}
        for category, item_counts in self.items.items():
            for item_name, count in item_counts.items():
                item_list[item_name] = count
        return item_list

    def use_item(self,
                 item_name: str,
                 quantity: int = 1) -> Optional[models.Item]:
        """Use a consumable item from inventory.
        
        Returns the item, or None if not found or insufficient quantity.
        """
        inventory = self._get_inventory(item_name)
        # Check if item exists and has enough quantity
        if item_name not in inventory:
            print(f"{item_name} not found in inventory.")
            return None
        if inventory[item_name] < quantity:
            print(f"Not enough {item_name} to use.")
            return None
        inventory[item_name] -= quantity
        if inventory[item_name] == 0:
            del inventory[item_name]
        return models.create_item(item_name)

    def remove_item(self, item_name: str, quantity: int = 1) -> None:
        """Remove an item completely from inventory."""
        self.use_item(item_name, quantity)

    def to_string(self) -> str:
        """Return a formatted string of the inventory."""
        if not self.items:
            return "Inventory is empty."

        lines: list[str] = ["╔═ Inventory ═══════════════╗"]

        # Weapon
        weapon = self.items.get("Weapon", "None")
        lines.append(f"  Weapon       » {weapon}")

        # Armour
        lines.append("  Armour")
        armour = self.items.get("Armour", {})
        for part in ["Helmet", "Chestplate", "Leggings", "Boots"]:
            equipped = armour.get(part, "None")
            lines.append(f"    {part:<11} » {equipped}")

        # Consumables
        lines.append("  Consumables")
        consumables = self.items.get("Consumables", {})
        if consumables:
            for item, qty in consumables.items():
                lines.append(f"    {item:<11} » x{qty}")
        else:
            lines.append("    None")

        lines.append("╚═══════════════════════════╝")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the inventory."""
        return self.items.copy()
