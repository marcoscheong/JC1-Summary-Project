# Combat module - CombatSequence and combat helper functions

import random

from campusmud import text
from campusmud.models import Ability
from campusmud.entities import Player, Monster

BOSS_NAME = "Origin of Chaos"


class CombatSequence:
    """Manages turn-based combat between player and monster."""
    def __init__(
        self,
        player: Player,
        monster: Monster,
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

    def start_sequence(self, is_boss: bool = False) -> str:
        """Run combat sequence for normal monsters."""
        while self.current_turn <= self.max_turns:
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            print(f"\n===== Turn {self.current_turn} =====\n")
            print(
                f"Player Health:  {text.health_bar(self.player.current_health, self.player.max_health)}\n"
                f"Monster Health: {text.health_bar(self.monster.current_health, self.monster.max_health)}"
            )

            print(f"Player Elixir: {p_elixir} | {'Boss' if is_boss else 'Monster'} Elixir: {m_elixir}\n")

            # Choose abilities
            player_seq = self.player_ability_sequence(p_elixir)
            monster_seq = self.monster_ability_sequence(m_elixir)

            # Aggregate totals
            p_total_attack = sum(a.attack for a in player_seq)
            p_total_shield = sum(a.shield for a in player_seq)
            p_total_heal = sum(a.heal for a in player_seq)
            p_total_save = sum(a.saved_elixir for a in player_seq)

            m_total_attack = sum(a.attack for a in monster_seq)
            m_total_shield = sum(a.shield for a in monster_seq)
            m_total_heal = sum(a.heal for a in monster_seq)
            m_total_save = sum(a.saved_elixir for a in monster_seq)

            # Compute damage after shields
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.calculate_atk() / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.attack / 10))
            m_total_heal = max(0, m_total_heal) * self.monster.attack / 10
            p_total_heal = max(0, p_total_heal) * self.player.calculate_atk() / 10

            # Apply effects
            self.monster.take_damage(dmg_to_monster)
            self.player.take_damage(dmg_to_player)
            self.player.heal(p_total_heal)
            self.monster.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

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

            if dmg_to_player > 0: print(f"Damage to Player: {text.format_number(dmg_to_player)}")
            if dmg_to_monster > 0: print(f"Damage to Monster: {text.format_number(dmg_to_monster)}")
            if p_total_heal > 0: print(f"Player Healed: {text.format_number(p_total_heal)}")
            if m_total_heal > 0: print(f"Monster Healed: {text.format_number(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Monster: {self.saved_m}")
            print(f"Health Status -> Player: {text.format_number(self.player.current_health)} | "
                f"{'Boss' if is_boss else 'Monster'}: {text.format_number(self.monster.current_health)}")

            # Next turn
            input("\nPress Enter to continue...")
            self.current_turn += 1
            text.clear_screen()

            if self.player.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # End of sequence winner
        if self.player.current_health > self.monster.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'

    def start_boss_sequence(self) -> str:
        """
        Run combat sequence for boss with elixir steal and shared fate mechanics.
        """
        while self.current_turn <= self.max_turns:
            # Calculate elixir
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            # Display turn header
            print(f"\n===== Turn {self.current_turn} =====\n")
            
            # Boss steals elixir
            steal_amount = random.randint(0, p_elixir // 3)
            p_elixir -= steal_amount
            m_elixir += steal_amount
            if steal_amount > 0:
                print(f"{BOSS_NAME} steals {steal_amount} elixir from you!")

            print(
                f"Player Health: {text.health_bar(self.player.current_health, self.player.max_health)}\n"
                f"Boss Health:   {text.health_bar(self.monster.current_health, self.monster.max_health)}"
            )

            print(f"Player Elixir: {p_elixir} | Boss Elixir: {m_elixir}\n")

            # Player & Boss choose abilities
            player_seq = self.player_ability_sequence(p_elixir)
            monster_seq = self.monster_ability_sequence(m_elixir)

            # Aggregate totals
            p_total_attack = sum(a.attack for a in player_seq)
            p_total_shield = sum(a.shield for a in player_seq)
            p_total_heal = sum(a.heal for a in player_seq)
            p_total_save = sum(a.saved_elixir for a in player_seq)

            m_total_attack = sum(a.attack for a in monster_seq)
            m_total_shield = sum(a.shield for a in monster_seq)
            m_total_heal = sum(a.heal for a in monster_seq)
            m_total_save = sum(a.saved_elixir for a in monster_seq)
            
            # Compute damage with shared fate
            shared_fate_percent = 0.25
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.calculate_atk() / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.attack / 10))

            dmg_to_monster_total = dmg_to_monster * (1 + shared_fate_percent)
            dmg_to_player_total = dmg_to_player * (1 + shared_fate_percent)

            # Apply effects
            self.monster.take_damage(dmg_to_monster_total)
            self.player.take_damage(dmg_to_player_total)
            self.player.heal(p_total_heal)
            self.monster.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

            # Special shared fate every 3rd turn
            if self.current_turn % 3 == 0:
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

            boss_abilities = []
            if m_total_attack > 0: boss_abilities.append(f"Attack {m_total_attack}")
            if m_total_shield > 0: boss_abilities.append(f"Shield {m_total_shield}")
            if m_total_heal > 0: boss_abilities.append(f"Heal {m_total_heal}")

            text.clear_screen()

            print(text.combat_spacing_text)
            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Boss Abilities: {' | '.join(boss_abilities)}\n")

            print(f"Damage to Boss: {text.format_number(dmg_to_monster_total)}")
            print(f"Damage to Player: {text.format_number(dmg_to_player_total)}")
            print(f"Player Healed: {text.format_number(p_total_heal)}")
            print(f"Boss Healed: {text.format_number(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Boss: {self.saved_m}")
            print(f"Health Status -> Player: {text.format_number(self.player.current_health)} | Boss: {text.format_number(self.monster.current_health)}")

            # Next turn
            input("\nPress Enter to continue...")
            self.current_turn += 1
            text.clear_screen()

            # Mid-turn death check
            if self.player.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # End-of-sequence winner
        if self.player.current_health > self.monster.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'

    def player_ability_sequence(self, elixir: int) -> list[Ability]:
        """Get player to choose actions and their magnitudes."""
        ability_sequence: list[Ability] = []
        available_elixir: int = elixir
        ability_dict = {a.name: a for a in self.player.abilities}
        
        cheapest_cost: int = text.cheapest_ability_cost

        while available_elixir >= cheapest_cost:
            print('Elixir: ' + str(available_elixir) + '\n')

            available_abilities = []

            for ability in self.player.abilities:
                if ability.elixir <= available_elixir:
                    available_abilities.append(ability)

            choice = text.prompt_player_choice(
                preamble="Your available moves: ",
                choices=[a.name for a in available_abilities],
                prompt=text.input_prompt
            )           
            ability = Ability(ability_dict[choice].name)
            magnitude: int = 0
            while True:
                magnitude_input = input(text.magnitude_prompt)
                if magnitude_input.isdigit():
                    magnitude = int(magnitude_input)
                    if magnitude <= available_elixir:
                        break
                print(text.input_error_prompt)
            
            if choice == "attack":
                ability.attack = magnitude
            elif choice == "shield":
                ability.shield = magnitude
            elif choice == "heal":
                ability.heal = magnitude
            elif choice == "save":
                ability.saved_elixir = magnitude
            
            ability.magnitude = magnitude
            ability_sequence.append(ability)
            available_elixir -= magnitude
        
        return ability_sequence

    def monster_ability_sequence(self, elixir: int) -> list[Ability]:
        """
        Generate random monster behavior for choosing actions and magnitudes.
        """
        ability_sequence = []
        available_elixir = elixir

        cheapest_cost = text.cheapest_ability_cost

        while available_elixir >= cheapest_cost:
            original = random.choices(self.monster.abilities, text.monster_ability_weights)[0]
            a = Ability(original.name)
            if a.elixir <= available_elixir:
                magnitude = random.randint(1, available_elixir)
                if a.name == "attack":
                    a.attack = magnitude
                    a.magnitude = magnitude
                elif a.name == "shield":
                    a.shield = magnitude
                    a.magnitude = magnitude
                elif a.name == "heal":
                    a.heal = magnitude
                    a.magnitude = magnitude
                elif a.name == "save":
                    a.saved_elixir = magnitude
                    a.magnitude = magnitude
                available_elixir -= magnitude
                ability_sequence.append(a)
        
        return ability_sequence

    def end_sequence(self) -> str:
        """End the combat once either player or enemy dies."""
        if self.player.current_health == 0:
            return 'defeat'
        elif self.monster.current_health == 0:
            return 'victory'
        return 'ongoing'
