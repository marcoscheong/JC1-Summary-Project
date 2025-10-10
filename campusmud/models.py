# Data models - pure data classes for game stats and drops
import random
import text


class Stats:
    """
    Holds character stats (health, attack) with damage and heal methods.
    """
    def __init__(self, max_health, attack):
        self.max_health = max_health
        self.attack = attack
        self.current_health = max_health
    
    def take_damage(self, damage):
        """
        Reduce health by damage amount. Returns 'died' if health reaches zero.
        """
        if (self.current_health - damage) <= 0:
            self.current_health = 0
            return 'died'
        else:
            self.current_health -= damage
    
    def heal(self, healAmount):
        """
        Increase current health up to max_health.
        """
        self.current_health = min(self.current_health + healAmount, self.max_health)
    
    def return_stats(self):
        """
        Return a formatted string of the player's stats.
        """
        lines = ["╔═ Player Stats ═════════════╗"]
        lines.append(f"  Health      » {self.current_health}/{self.max_health}")
        lines.append(f"  Attack      » {self.attack}")
        lines.append("╚═══════════════════════════╝")
        return "\n".join(lines)


class Drop:
    """
    Represents loot dropped from monsters (weapon, armour, or consumable).
    """
    def __init__(self, weaponWeights, armourWeights):
        self.weaponWeights = weaponWeights
        self.armourWeights = armourWeights
        self.name = ''
    
    def generateDrop(self):
        """
        Randomly generate a weapon, armour, or consumable drop.
        """
        r = random.randint(0, 2)
        if r == 0:
            drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
            self.type = 'weapon'
        elif r == 1:
            drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
            self.type = 'armour'
        elif r == 2:
            number = random.randint(1, 3)
            if number == 1:
                drop = 'attack potion'
                self.type = 'consumable'
            elif number == 2:
                drop = 'health potion'
                self.type = 'consumable'
            else:
                drop = 'healing potion'
                self.type = 'consumable'
        self.drop = drop
        return self
    
    def generateArmourDrop(self):
        """
        Generate only an armour drop.
        """
        drop = random.choices(list(text.Armour.keys()), self.armourWeights)[0]
        self.type = 'armour'
        self.drop = drop
        return self
        
    
    def generateWeaponDrop(self):
        """
        Generate only a weapon drop.
        """
        drop = random.choices(list(text.Weapon.keys()), self.weaponWeights)[0]
        self.type = 'weapon'
        self.drop = drop
        return self


class Ability:
    """
    Represents a player action during combat (attack, shield, heal, save).
    """
    def __init__(self, name):
        self.name = name
        self.attack = 0
        self.shield = 0
        self.heal = 0
        self.elixir = 1
        self.saved_elixir = 0
        self.magnitude = 0
