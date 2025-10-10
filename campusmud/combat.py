# Combat module - CombatSequence and combat helper functions
import os
import random
import text
from campusmud.models import Ability


class CombatSequence:
    """
    Manages turn-based combat between player and monster.
    """
    def __init__(self, player, monster, base_elixir, max_turns):
        self.base_elixir = base_elixir
        self.current_turn = 1
        self.max_turns = max_turns

        self.player = player
        self.monster = monster

        self.saved_p = 0  # saved player elixir from each turn
        self.saved_m = 0  # saved monster elixir from each turn

    def _fmt(self, x):
        """
        Format numbers to 1 decimal if needed, no trailing .0.
        """
        return int(x) if isinstance(x, (int, float)) and float(x).is_integer() else round(x, 1)

    def start_sequence(self, is_boss=False):
        """
        Run combat sequence for normal monsters.
        """
        while self.current_turn <= self.max_turns:
            elixir = (self.base_elixir * self.current_turn) // 2
            p_elixir = elixir + self.saved_p
            m_elixir = elixir + self.saved_m
            self.saved_p = 0
            self.saved_m = 0

            print(f"\n===== Turn {self.current_turn} =====\n")
            print(
                f"Player Health:  {self.health_bar(self.player.stats.current_health, self.player.stats.max_health)}\n"
                f"Monster Health: {self.health_bar(self.monster.stats.current_health, self.monster.stats.max_health)}"
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
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.stats.attack / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.stats.attack / 10))
            m_total_heal = max(0, m_total_heal) * self.monster.stats.attack / 10
            p_total_heal = max(0, p_total_heal) * self.player.stats.attack / 10

            # Apply effects
            self.monster.stats.take_damage(dmg_to_monster)
            self.player.stats.take_damage(dmg_to_player)
            self.player.stats.heal(p_total_heal)
            self.monster.stats.heal(m_total_heal)
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

            os.system('clear')

            print(text.combat_spacing_text)
            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Monster Abilities: {' | '.join(monster_abilities)}\n")

            if dmg_to_player > 0: print(f"Damage to Player: {self._fmt(dmg_to_player)}")
            if dmg_to_monster > 0: print(f"Damage to Monster: {self._fmt(dmg_to_monster)}")
            if p_total_heal > 0: print(f"Player Healed: {self._fmt(p_total_heal)}")
            if m_total_heal > 0: print(f"Monster Healed: {self._fmt(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Monster: {self.saved_m}")
            print(f"Health Status -> Player: {self._fmt(self.player.stats.current_health)} | "
                f"{'Boss' if is_boss else 'Monster'}: {self._fmt(self.monster.stats.current_health)}")

            # Next turn
            input("\nPress Enter to continue...")
            self.current_turn += 1
            os.system('clear')

            if self.player.stats.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.stats.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # End of sequence winner
        if self.player.stats.current_health > self.monster.stats.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'

    def start_boss_sequence(self):
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
                print(f"{text.boss_monster} steals {steal_amount} elixir from you!")
            
            print(
                f"Player Health: {self.health_bar(self.player.stats.current_health, self.player.stats.max_health)}\n"
                f"Boss Health:   {self.health_bar(self.monster.stats.current_health, self.monster.stats.max_health)}"
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
            dmg_to_monster = max(0, (p_total_attack - m_total_shield) * (self.player.stats.attack / 10))
            dmg_to_player = max(0, (m_total_attack - p_total_shield) * (self.monster.stats.attack / 10))

            dmg_to_monster_total = dmg_to_monster * (1 + shared_fate_percent)
            dmg_to_player_total = dmg_to_player * (1 + shared_fate_percent)

            # Apply effects
            self.monster.stats.take_damage(dmg_to_monster_total)
            self.player.stats.take_damage(dmg_to_player_total)
            self.player.stats.heal(p_total_heal)
            self.monster.stats.heal(m_total_heal)
            self.saved_p = p_total_save
            self.saved_m = m_total_save

            # Special shared fate every 3rd turn
            if self.current_turn % 3 == 0:
                self.player.stats.take_damage(dmg_to_monster)
                self.monster.stats.take_damage(dmg_to_player)
                self.monster.stats.heal(p_total_heal)
                self.player.stats.heal(m_total_heal)
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

            os.system('clear')

            print(text.combat_spacing_text)
            print(f"Player Abilities: {' | '.join(player_abilities)}")
            print(f"Boss Abilities: {' | '.join(boss_abilities)}\n")

            print(f"Damage to Boss: {self._fmt(dmg_to_monster_total)}")
            print(f"Damage to Player: {self._fmt(dmg_to_player_total)}")
            print(f"Player Healed: {self._fmt(p_total_heal)}")
            print(f"Boss Healed: {self._fmt(m_total_heal)}")
            print(f"Saved Elixir  -> Player: {self.saved_p} | Boss: {self.saved_m}")
            print(f"Health Status -> Player: {self._fmt(self.player.stats.current_health)} | Boss: {self._fmt(self.monster.stats.current_health)}")

            # Next turn
            input("\nPress Enter to continue...")
            self.current_turn += 1
            os.system('clear')

            # Mid-turn death check
            if self.player.stats.current_health <= 0:
                print(text.defeat_text)
                return 'defeat'
            if self.monster.stats.current_health <= 0:
                print(text.victory_text)
                return 'victory'

        # End-of-sequence winner
        if self.player.stats.current_health > self.monster.stats.current_health:
            print(text.victory_text)
            return 'victory'
        else:
            print(text.defeat_text)
            return 'defeat'

    def player_ability_sequence(self, elixir):
        """
        Get player to choose actions and their magnitudes.
        """
        ability_sequence = []
        available_elixir = elixir
        ability_dict = {a.name: a for a in self.player.abilities}
        
        cheapest_cost = text.cheapest_ability_cost

        while available_elixir >= cheapest_cost:
            print('Elixir: ' + str(available_elixir) + '\n')

            available_abilities = []

            for ability in self.player.abilities:
                if ability.elixir <= available_elixir:
                    available_abilities.append(ability)

            print(text.combat_sequence_prompt)
            for i, ability in enumerate(available_abilities):
                print(f"{i + 1}. {ability.name}")

            choice = input(text.input_prompt).strip().lower()

            if choice.isdigit():
                choice = int(choice)
                if 0 < choice <= len(available_abilities):
                    choice = available_abilities[choice - 1].name.strip().lower()
            
            if choice in [a.name for a in available_abilities]:
                ability = Ability(ability_dict[choice].name)
                magnitude = 100  # placeholder
                while magnitude > available_elixir:
                    magnitude = input(text.magnitude_prompt)
                    if not magnitude.isdigit():
                        print(text.input_error_prompt)
                        magnitude = 100
                    elif magnitude.isdigit():
                        magnitude = int(magnitude)
                        if magnitude > available_elixir:
                            print(text.input_error_prompt)
                
                if choice == "attack":
                    ability.attack = magnitude
                    ability.magnitude = magnitude
                elif choice == "shield":
                    ability.shield = magnitude
                    ability.magnitude = magnitude
                elif choice == "heal":
                    ability.heal = magnitude
                    ability.magnitude = magnitude
                elif choice == "save":
                    ability.saved_elixir = magnitude
                    ability.magnitude = magnitude
                
                ability_sequence.append(ability)
                available_elixir -= magnitude
            else:
                print(text.ability_addition_error)
        
        return ability_sequence

    def monster_ability_sequence(self, elixir):
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

    def returnMonsterDrop(self):
        """
        Return what the monster drops when killed.
        """
        return self.monster.drop

    def end_sequence(self):
        """
        End the combat once either player or enemy dies.
        """
        if self.player.stats.current_health == 0:
            print(text.defeat_text)
            return 'defeat'
        elif self.monster.stats.current_health == 0:
            print(text.victory_text)
            return 'victory'
        input('Press enter to continue...')

    def health_bar(self, current, maximum, bar_length=20):
        """
        Return a string representing a health bar.
        """
        if maximum <= 0:
            ratio = 0
        else:
            ratio = current / maximum
        filled_length = int(bar_length * ratio)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        return f"[{bar}] {current}/{maximum}"
