# Main entry point for Campus MUD

import sys

from campusmud.game import Game
import campusmud.text as text


class SplashScreen:
    """Splash screen for the Campus MUD game."""

    def __init__(self):
        pass

    def prompt_main_menu(self):
        """Display the main menu and return the player's choice."""
        choice = text.prompt_player_choice(
            preamble=text.welcome_prompt,
            choices=['start', 'load', 'quit', 'how to play'],
        )
        return choice


if __name__ == "__main__":
    splash = SplashScreen()
    choice = None
    while choice != 'quit':
        choice = splash.prompt_main_menu()
        if choice == 'start':
            game = Game()
            game.run()
        elif choice == 'load':
            game = Game()
            game.load_game()
            game.run()
        elif choice == 'how to play':
            print(text.how_to_play_text)
        elif choice == 'quit':
            print(text.thanks_message)
            sys.exit()
