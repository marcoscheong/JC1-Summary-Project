# Import statements
import mud
if __name__ == "__main__":
    game = mud.Game()
    #mud.welcome()
    #player = data.create_player()
    #game.add_player(player)
    while True:
        choices = game.get_options()
        command = game.prompt_player_choice(choices).strip().lower()
        if command in ['quit', 'exit']:
            #initiate exit
            pass
        elif command.startswith('go'):
            direction = command.split()[1]
            mud.maze.travel_to(direction)
        elif command.startswith('open'):
            #open chest
            pass
        elif command.startswith('fight'):
            #fight monster
            pass
        else:
            #print ABSTRACTED error message
            pass




        #choices = game.get_options()
        #choice = mud.prompt_player_choice(choices)
        #actions = game.get_actions(choices, choice)
        #game.execute(actions)
        #data.display(game.status())
    #mud.epilogue()