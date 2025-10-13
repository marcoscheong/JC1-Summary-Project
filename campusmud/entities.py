# Entities - Character, Player, Monster, and Inventory classes

from typing import Optional

from campusmud import config, models, text
from campusmud.data import load_game_data
from campusmud.storage import Storage

game_data = load_game_data()

# Constants
BOSS_NAME = "Origin of Chaos"

# Enums
MOVES = list(game_data["moves"])
CONSUMABLES = list(game_data["items"]["consumables"].keys())
WEAPONS = list(game_data["items"]["weapons"].keys())
ARMOR = list(game_data["items"]["armor"].keys())


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
        max_health=monster_data["max_health"],
        attack=monster_data["attack"]
    )

def create_player() -> "Player":
    """Factory function to create a Player instance with default stats."""
    return Player(
        max_health=game_data["player"]["max_health"],
        attack=game_data["player"]["attack"],
    )


class Character:
    """
    Base class for all characters (player and monsters).
    """
    def __init__(self, max_health: int, attack: int) -> None:
        self.max_health: int = max_health
        self.attack: int = attack
        self.current_health: int = max_health
        self.abilities = [
            name for name in MOVES
        ]

    def take_damage(self, damage: int) -> str:
        """Reduce health by damage amount. Returns 'died' if health reaches zero.
        """
        if (self.current_health - damage) <= 0:
            self.current_health = 0
            return 'died'
        else:
            self.current_health -= damage
            return 'alive'

    def heal(self, healAmount: int) -> None:
        """Increase current health up to max_health."""
        self.current_health = min(self.current_health + healAmount, self.max_health)

    def return_stats(self) -> str:
        """Return a formatted string of the player's stats."""
        lines: list[str] = ["╔═ Player Stats ═════════════╗"]
        lines.append(f"  Health      » {self.current_health}/{self.max_health}")
        lines.append(f"  Attack      » {self.attack}")
        lines.append("╚═══════════════════════════╝")
        return "\n".join(lines)


class Player(Character):
    """Player character with inventory and stat management."""

    def __init__(self, max_health: int, attack: int) -> None:
        super().__init__(max_health, attack)
        self.inventory: Optional[Inventory] = None
        self.base_atk: int = attack
        self.base_health: int = max_health
        self.armor = {
            "Helmet": None,
            "Chestplate": None,
            "Leggings": None,
            "Boots": None
        }
        self.weapon: Optional[models.Weapon] = None

    def calculate_atk(self) -> int:
        """Calculate total attack including weapon bonus."""
        if self.weapon:
            return self.base_atk + self.weapon.attack_bonus
        return self.base_atk

    def calculate_def(self) -> int:
        """Calculate total defense including armor bonus."""
        if self.armor:
            return self.armor.defense_bonus
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
        print(f"{armor.name} equipped.")
        print(text.equip_spacing_text + '\n')
        self.inventory.remove_item(armor.name)
        self.inventory.save_inventory()
        return True

    def equip_weapon(self, weapon: models.Weapon) -> bool:
        self.weapon = weapon
        print('\n' + text.equip_spacing_text)
        print(f"{weapon.name} has been equipped.")
        print(text.equip_spacing_text + '\n')
        self.inventory.remove_item(weapon.name)
        self.inventory.save_inventory()
        return True

    def create_new_storage(self, storage: Storage, file: str) -> None:
        """Create a new empty storage for the player."""
        default_data = storage.get_data(config.DEFAULT_SAVE_FILE)
        storage.save_data(file, default_data)
        self.load_from_storage(storage, file)

    def load_from_storage(self, storage: Storage, file: str) -> None:
        """Load player data from a saved file."""
        data = storage.get_data(file)
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: Expected a dictionary.")

        self.max_health = int(data.get("Player_max_health", self.base_health))
        self.current_health = int(data.get("Player_current_health", self.base_health))
        self.attack = int(data.get("Player_attack", self.base_atk))
        self.inventory = Inventory(storage, file)
        self.recalculate_stats()

    def save_to_storage(self, storage: Storage, file: str) -> None:
        """Save player data to a file."""
        if self.inventory:
            storage.save_data(file, {
                "Player_max_health": self.max_health,
                "Player_current_health": self.current_health,
                "Player_attack": self.attack
            })
            self.inventory.save_inventory()
    
    def show_inventory(self) -> None:
        """Display the player's inventory."""
        if self.inventory:
            print(self.inventory.return_inventory())
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


class Monster(Character):

    def __init__(self, max_health: int, attack: int) -> None:
        super().__init__(max_health, attack)


class Inventory:
    """Player inventory with weapons, armour, and consumables."""

    def __init__(self, storage: Storage, file: str) -> None:
        self.storage: Storage = storage
        self.file: str = file
        try:
            data = self.storage.get_data(file)
            self.items: dict = data.get("Items", {})
        except FileNotFoundError:
            self.items = {}
        
        # Ensure canonical shape always exists
        if "Weapon" not in self.items:
            self.items["Weapon"] = None
        if "Armour" not in self.items:
            self.items["Armour"] = {}
        if "Consumables" not in self.items:
            self.items["Consumables"] = {}
        
        self.save_inventory()

    def add_item(self, item_name: str, quantity: int = 1) -> None:
        """Add an item to inventory."""
        if item_name in text.Consumable.keys():
            if item_name in self.items["Consumables"]:
                self.items["Consumables"][item_name] += quantity
            else:
                self.items["Consumables"][item_name] = quantity
        else:
            if item_name in self.items:
                self.items[item_name] += quantity
            else:
                self.items[item_name] = quantity
        self.save_inventory()

    def list_items(self) -> list[str]:
        """List all items in inventory."""
        item_list: list[str] = []
        for category, items in self.items.items():
            if isinstance(items, dict):
                for item, qty in items.items():
                    item_list.append(f"{item} x{qty}")
            else:
                item_list.append(f"{items}")
        return item_list

    def use_item(self, item_name: str, quantity: int = 1) -> bool:
        """Use a consumable item from inventory."""
        if item_name not in self.items["Consumables"]:
            print(f"{item_name} not found in inventory.")
            return False
        if self.items["Consumables"][item_name] < quantity:
            print(f"Not enough {item_name} to use.")
            return False
        
        self.items["Consumables"][item_name] -= quantity
        if self.items["Consumables"][item_name] <= 0:
            del self.items["Consumables"][item_name]
        self.save_inventory()
        return True
    
    def remove_item(self, item_name: str) -> None:
        if item_name in self.items:
            del self.items[item_name]
            self.save_inventory()
        else:
            print(f"{item_name} not found in inventory.")

    def save_inventory(self) -> None:
        """Save inventory to the JSON file."""
        try:
            data = self.storage.get_data(self.file)
        except FileNotFoundError:
            data = {}
        data["Items"] = self.items
        self.storage.save_data(self.file, data)

    def return_inventory(self) -> str:
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
