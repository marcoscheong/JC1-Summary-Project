# Import statements
import mud
import text
import sys

if __name__ == "__main__":
    game = mud.Game()
    game.set_state('start')
    game.welcome()

    #player = data.create_player()
    #game.add_player(player)
    while True:
        print(text.printing_text_spacing)
        choices = game.get_options()
        command = game.prompt_player_choice(choices).strip().lower()
        if command.isdigit():
            if int(command) >= len(choices):
                print('length of choices: ' + str(len(choices)))
                print(text.input_error_prompt)
            else:
                command = choices[int(command) - 1]
        if command in ['quit', 'exit']:
            print(text.thanks_message)
            sys.exit()
        elif command.startswith('go'):
            direction = command.split()[1]
            if direction in text.directions:
                game.maze.travel_to(direction)
            else:
                print(text.input_error_prompt)
        elif command.startswith('open'):
            if type(game.get_maze.current_room) == mud.TreasureRoom:
                #open chest
                pass
            pass
        elif command.startswith('fight'):
            #fight monster
            pass
        else:
            #print ABSTRACTED error message
            print(text.input_error_prompt)

        if game.game_state == 'travel':
            game.maze.draw_rooms()
        #choices = game.get_options()
        #choice = mud.prompt_player_choice(choices)
        #actions = game.get_actions(choices, choice)
        #game.execute(actions)
        #data.display(game.status())
    #mud.epilogue()