# Main entry point for Campus MUD

import sys

from labyrinth.game import Game
import labyrinth.text as text


class SplashScreen:
    """Splash screen for the Campus MUD game."""

    def __init__(self) -> None:
        pass

    def prompt_main_menu(self) -> str:
        """Display the main menu and return the player's choice."""
        choice = text.prompt_player_choice(
            preamble=text.welcome_prompt,
            choices=['start', 'load', 'quit', 'how to play'],
        )
        return choice


if __name__ == "__main__":
    splash: SplashScreen = SplashScreen()
    choice: str | None = None
    while choice != 'quit':
        choice = splash.prompt_main_menu()
        if choice == 'start':
            game: Game = Game()
            game.run()
        elif choice == 'load':
            game = Game.load_from_data()
            game.run()
        elif choice == 'how to play':
            print(text.how_to_play_text)
    print(text.thanks_message)
    sys.exit()
