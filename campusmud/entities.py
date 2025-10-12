# Entities - Character, Player, Monster, and Inventory classes
from campusmud import text
from campusmud.storage import Storage
from campusmud.models import Stats, Ability


class Character:
    """
    Base class for all characters (player and monsters).
    """
    def __init__(self, stats):
        self.stats = stats
        self.abilities = []
        for a in text.move_pool:
            self.abilities.append(Ability(a))


class Player(Character):
    """
    Player character with inventory and stat management.
    """
    def __init__(self, stats):
        super().__init__(stats)
        self.inventory = None
        self.base_atk = text.default_attack
        self.base_health = text.default_health

    def create_new_storage(self, storage, file):
        """
        Create a new empty storage for the player.
        """
        default_data = storage.get_data(text.default_save_file)
        storage.save_data(file, default_data)
        self.load_from_storage(storage, file)

    def load_from_storage(self, storage, file):
        """
        Load player data from a saved file.
        """
        data = storage.get_data(file)
        self.stats.max_health = data["Player_max_health"]
        self.stats.current_health = data["Player_current_health"]
        self.stats.attack = data["Player_attack"]
        self.inventory = Inventory(storage, file)
        self.recalculate_stats()

    def save_to_storage(self, storage, file):
        """
        Save player data to a file.
        """
        storage.save_data(file, {
            "Player_max_health": self.stats.max_health,
            "Player_current_health": self.stats.current_health,
            "Player_attack": self.stats.attack
        })
        self.inventory.save_inventory()
    
    def show_inventory(self):
        """
        Display the player's inventory.
        """
        if self.inventory:
            self.inventory.show_inventory()
        else:
            print("No inventory loaded.")
    
    def atk_potion(self, amt):
        """
        Increase player's base attack.
        """
        self.base_atk += amt
    
    def health_potion(self, amt):
        """
        Increase player's base health.
        """
        self.base_health += amt

    def recalculate_stats(self):
        """
        Recalculate stats based on equipped items and base stats.
        """
        # Reset attack and health back to base
        self.stats.attack = self.base_atk
        old_max_health = self.stats.max_health
        old_current_health = self.stats.current_health

        weapon = self.inventory.items.get("Weapon", None)
        attack_bonus = text.Weapon.get(weapon, 0) if weapon else 0

        armour = self.inventory.items.get("Armour", {})
        defence_bonus = sum(text.Armour.get(part, 0) for part in armour.values() if part)

        self.stats.attack = self.base_atk + attack_bonus
        self.stats.max_health = self.base_health + defence_bonus

        if old_max_health > 0:
            health_ratio = old_current_health / old_max_health
        else:
            health_ratio = 1.0

        self.stats.current_health = round(self.stats.max_health * health_ratio, 1)

        # Ensure it never goes above max
        if self.stats.current_health > self.stats.max_health:
            self.stats.current_health = self.stats.max_health


class Monster(Character):
    """
    Monster character - inherits from Character.
    """
    def __init__(self, stats):
        super().__init__(stats)


class Inventory:
    """
    Player inventory with weapons, armour, and consumables.
    """
    def __init__(self, storage, file):
        self.storage = storage
        self.file = file
        try:
            data = self.storage.get_data(file)
            self.items = data.get("Items", {})
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

    def add_item(self, item_name, quantity=1):
        """
        Add an item to inventory.
        """
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
        item_list = []
        for category, items in self.items.items():
            if isinstance(items, dict):
                for item, qty in items.items():
                    item_list.append(f"{item} x{qty}")
            else:
                item_list.append(f"{items}")
        return item_list

    def use_item(self, item_name, quantity=1):
        """
        Use a consumable item from inventory.
        """
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
    
    def equip_weapon(self, weapon_name):
        """
        Equip a weapon.
        """
        if weapon_name in text.Weapon.keys():
            self.items["Weapon"] = weapon_name
            print('\n' + text.equip_spacing_text)
            print(f"{weapon_name} has been equipped.")
            print(text.equip_spacing_text + '\n')
            self.save_inventory()
        else:
            print(f"{weapon_name} not found.")
            return False
    
    def equip_armour(self, slot, armour_name):
        """
        Equip armour to a specific slot.
        """
        if armour_name in text.Armour:
            if "Armour" not in self.items:
                self.items["Armour"] = {}
            self.items["Armour"][slot] = armour_name
            print('\n' + text.equip_spacing_text)
            print(f"{armour_name} equipped in {slot}.")
            print(text.equip_spacing_text + '\n')
            self.save_inventory()
        else:
            print(f"{armour_name} not found.")
            return False

    def remove_item(self, item_name):
        """
        Remove an item completely from inventory.
        """
        if item_name in self.items:
            del self.items[item_name]
            self.save_inventory()
        else:
            print(f"{item_name} not found in inventory.")

    def save_inventory(self):
        """
        Save inventory to the JSON file.
        """
        try:
            data = self.storage.get_data(self.file)
        except FileNotFoundError:
            data = {}
        data["Items"] = self.items
        self.storage.save_data(self.file, data)

    def return_inventory(self):
        """
        Return a formatted string of the inventory.
        """
        if not self.items:
            return "Inventory is empty."

        lines = ["╔═ Inventory ═══════════════╗"]

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
