# Import statements
import mud

import data

if __name__ == "__main__":
    game = mud.Game()
    mud.welcome()
    player = data.create_player()
    game.add_player(player)
    while not game.is_gameover():
        choices = game.get_options()
        choice = data.prompt_player_choice(choices)
        actions = game.get_actions(choice)
        game.execute(actions)
        data.display(game.status())
    mud.epilogue()