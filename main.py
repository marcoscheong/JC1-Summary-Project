# Import statements
import mud
import text
if __name__ == "__main__":
    game = mud.Game()
    #mud.welcome()
    #player = data.create_player()
    #game.add_player(player)
    while True:
        choices = game.get_options()
        command = game.prompt_player_choice(choices).strip().lower()
        if command in ['quit', 'exit']:
            print(text.thanks_message)
            
            #initiate exit
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
            print(text.input_error_prompt)




        #choices = game.get_options()
        #choice = mud.prompt_player_choice(choices)
        #actions = game.get_actions(choices, choice)
        #game.execute(actions)
        #data.display(game.status())
    #mud.epilogue()