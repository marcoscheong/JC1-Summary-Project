# Combat module - CombatSequence and combat helper functions

import random

from campusmud import config, entities, text
from campusmud.data import load_game_data
from campusmud.entities import Player, Monster


game_data = load_game_data()
BOSS_NAME = "Origin of Chaos"
MOVES = game_data["moves"]


class Action:
    """Represents a player action during combat (attack, shield, heal, save).

    Players can choose the amount of elixir to allocate to each action.
    """

    def __init__(self, name: str, cost: int, elixir: int) -> None:
        self.name = name
        self.cost = cost
        self.elixir = elixir


class Attack(Action):
    """Represents an attack action."""
    def __init__(self, cost: int, elixir: int) -> None:
        super().__init__("Attack", cost, elixir)


class Shield(Action):
    """Represents a shield action."""
    def __init__(self, cost: int, elixir: int) -> None:
        super().__init__("Shield", cost, elixir)


class Heal(Action):
    """Represents a heal action."""
    def __init__(self, cost: int, elixir: int) -> None:
        super().__init__("Heal", cost, elixir)


class Save(Action):
    """Represents a save action.

    Saves elixir for next turn.
    """
    def __init__(self, cost: int, elixir: int) -> None:
        super().__init__("Save", cost, elixir)


def create_action(name: str, elixir: int) -> Action:
    """Factory function to create an Action by name."""
    if name == "attack":
        return Attack(MOVES["attack"]["cost"], elixir)
    if name == "shield":
        return Shield(MOVES["shield"]["cost"], elixir)
    if name == "heal":
        return Heal(MOVES["heal"]["cost"], elixir)
    if name == "save":
        return Save(MOVES["save"]["cost"], elixir)
    else:
        raise ValueError(f"Action '{name}' not found.")


def choose_actions(character: entities.Character,
                   available_elixir: int) -> list[Action]:
    """Generate list of actions for the character."""
    actions: list[Action] = []
    lowest_cost = min([
        MOVES[name]["cost"] for name in character.abilities
    ])

    while available_elixir >= lowest_cost:
        print('Elixir: ' + str(available_elixir) + '\n')
        if isinstance(character, entities.Player):
            choice = text.prompt_player_choice(
                preamble="Your available moves: ",
                choices=[
                    name for name in character.abilities
                    if MOVES[name]["cost"] <= available_elixir
                ],
                prompt=text.input_prompt
            )           
            number = text.prompt_number_input(
                prompt=text.magnitude_prompt,
                min_value=1,
                max_value=available_elixir
            )
        elif isinstance(character, entities.Monster):
            choice = random.choices(
                character.abilities,
                config.WEIGHTS["monster_ability"]
            )[0]
            number = random.randint(1, available_elixir)
        else:
            raise ValueError(f"Unknown character type: {character}")
        ability = create_action(name=choice, elixir=number)
        actions.append(ability)
        available_elixir -= ability.elixir
    
    return actions


def calculate_damage(attacker_attack: int,
                     defender_shield: int) -> int:
    """Calculate damage dealt from attacker to defender after shield."""
    if attacker_attack <= defender_shield:
        return 0
    else:
        return round(attacker_attack - defender_shield * 0.1)


def calculate_heal(character_heal: int, character_attack: int) -> int:
    """Calculate healing done by a character."""
    if character_heal <= 0:
        return 0
    else:
        return round(character_heal * character_attack * 0.1)


class CombatSequence:
    """Manages turn-based combat between player and monster."""
    def __init__(
        self,
        player: entities.Player,
        monster: entities.Monster,
        base_elixir: int,
        max_turns: int
    ) -> None:
        self.base_elixir: int = base_elixir
        self.current_turn: int = 1
        self.max_turns: int = max_turns

        self.player: Player = player
        self.monster: Monster = monster

        self.saved_p: int = 0  # saved player elixir from each turn
        self.saved_m: int = 0  # saved monster elixir from each turn

    def run_combat(self, elixir_steal: bool = False, shared_fate: float = 0.0) -> entities.Character:
        """Run combat sequence."""
        while (
                self.current_turn <= self.max_turns
                and not (self.player.is_dead() or self.monster.is_dead())
        ):
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            print(f"\n===== Turn {self.current_turn} =====\n")

            if elixir_steal:
                steal_amount = random.randint(0, p_elixir // 3)
                p_elixir -= steal_amount
                m_elixir += steal_amount
                if steal_amount > 0:
                    print(f"{self.monster.name} steals {steal_amount} elixir from you!")
            print(
                f"Player Health:  {text.health_bar(self.player.current_health, self.player.max_health)}\n"
                f"Monster Health: {text.health_bar(self.monster.current_health, self.monster.max_health)}"
            )

            print(f"{self.player.name} Elixir: {p_elixir} | {self.monster.name} Elixir: {m_elixir}\n")

            # Choose abilities
            player_actions = choose_actions(self.player, p_elixir)
            monster_actions = choose_actions(self.monster, m_elixir)

            # Aggregate totals

            p_total_attack = sum(a.elixir for a in player_actions if isinstance(a, Attack))
            p_total_shield = sum(a.elixir for a in player_actions if isinstance(a, Shield))
            p_total_heal = sum(a.elixir for a in player_actions if isinstance(a, Heal))
            p_total_save = sum(a.elixir for a in player_actions if isinstance(a, Save))

            m_total_attack = sum(a.elixir for a in monster_actions if isinstance(a, Attack))
            m_total_shield = sum(a.elixir for a in monster_actions if isinstance(a, Shield))
            m_total_heal = sum(a.elixir for a in monster_actions if isinstance(a, Heal))
            m_total_save = sum(a.elixir for a in monster_actions if isinstance(a, Save))

            # Compute damage after shields, with shared fate modifier
            dmg_to_monster = calculate_damage(p_total_attack, m_total_shield)
            dmg_to_player = calculate_damage(m_total_attack, p_total_shield)
            m_total_heal = calculate_heal(m_total_heal, self.monster.calculate_atk())
            p_total_heal = calculate_heal(p_total_heal, self.player.calculate_atk())

            # Apply effects
            self.monster.take_damage(round(dmg_to_monster * (1 + shared_fate)))
            self.player.take_damage(round(dmg_to_player * (1 + shared_fate)))
            self.player.heal(p_total_heal)
            self.monster.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

            # Shared fate every 3rd turn if shared_fate is active
            if shared_fate != 0.0 and self.current_turn % 3 == 0:
                self.player.take_damage(dmg_to_monster)
                self.monster.take_damage(dmg_to_player)
                self.monster.heal(p_total_heal)
                self.player.heal(m_total_heal)
                print("Shared Fate Triggered! Effects mirrored this turn.")

            # Display turn summary
            player_abilities = []
            if p_total_attack > 0: player_abilities.append(f"Attack {p_total_attack}")
            if p_total_shield > 0: player_abilities.append(f"Shield {p_total_shield}")
            if p_total_heal > 0: player_abilities.append(f"Heal {p_total_heal}")
            if p_total_save > 0: player_abilities.append(f"Save {p_total_save}")

            monster_abilities = []
            if m_total_attack > 0: monster_abilities.append(f"Attack {m_total_attack}")
            if m_total_shield > 0: monster_abilities.append(f"Shield {m_total_shield}")
            if m_total_heal > 0: monster_abilities.append(f"Heal {m_total_heal}")
            if m_total_save > 0: monster_abilities.append(f"Save {m_total_save}")

            text.clear_screen()

            print(text.combat_spacing_text)
            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Monster Abilities: {' | '.join(monster_abilities)}\n")

            if dmg_to_player > 0: print(f"Damage to {self.player.name}: {text.format_number(dmg_to_player)}")
            if dmg_to_monster > 0: print(f"Damage to {self.monster.name}: {text.format_number(dmg_to_monster)}")
            if p_total_heal > 0: print(f"{self.player.name} Healed: {text.format_number(p_total_heal)}")
            if m_total_heal > 0: print(f"{self.monster.name} Healed: {text.format_number(m_total_heal)}")
            print(f"Saved Elixir  -> {self.player.name}: {self.saved_p} | {self.monster.name}: {self.saved_m}")
            print(f"Health Status -> {self.player.name}: {text.format_number(self.player.current_health)} | "
                f"{self.monster.name}: {text.format_number(self.monster.current_health)}")

            # Next turn
            text.linebreak()
            text.prompt_continue()
            self.current_turn += 1
            text.clear_screen()

        # End of sequence winner
        if self.player.is_dead():
            return self.monster
        elif self.monster.is_dead():
            return self.player
        elif self.player.current_health > self.monster.current_health:
            return self.player
        else:
            return self.monster
