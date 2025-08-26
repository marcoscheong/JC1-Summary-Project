# Import statements
import mud, sys, text, os

if __name__ == "__main__":
    game = mud.Game()
    game.set_state('start')
    game.welcome()

    #player = data.create_player()
    #game.add_player(player)
    while True:
        os.system('clear')

        if game.game_state == 'travel':
            game.maze.draw_rooms()

        if type(game.maze.current_room) == mud.TreasureRoom:
            if game.maze.current_room.claimed == False:
                print(text.treasure_room_text)
            else:
                print(text.claimed_treasure_room_text)
        elif type(game.maze.current_room) == mud.MonsterRoom:
            print(text.monster_room_text)
        choices = game.get_options()
        command = game.prompt_player_choice(choices).strip().lower()
        if command.isdigit():
            if int(command) > len(choices):
                print('length of choices: ' + str(len(choices)))
                print(text.input_error_prompt)
            else:
                command = choices[int(command) - 1].strip().lower()
        if command in ['quit', 'exit']:
            game.save_all_data(text.player_save_file)

            print(text.thanks_message)
            sys.exit()
        elif command in ['view inventory', 'inventory', 'inv']:
            os.system('clear')
            print(game.get_player().inventory.return_inventory())
            input('\nPress enter to continue...')
            os.system('clear')
        elif command.startswith('go'):
            direction = command.split()[1]
            if direction in text.directions:
                game.maze.travel_to(direction)
                game.save_all_data(text.player_save_file)
            else:
                print(text.input_error_prompt)
        elif command.startswith('open'):
            if type(game.get_maze().current_room) == mud.TreasureRoom:
                #open chest
                treasure_type = game.get_maze().current_room.get_type()
                drop = game.get_maze().current_room.get_drops()
                if treasure_type == 'weapon' or treasure_type == 'armour':
                    game.set_state('item chest')

                    print(f"You have found a {drop}!")

                    choices = game.get_options()
                    command = game.prompt_player_choice(choices).strip().lower()
                    if command.isdigit():
                        if int(command) > len(choices):
                            print(text.input_error_prompt)
                        else:
                            command = choices[int(command) - 1].strip().lower()
                    if command in ['go back', 'back']:
                        game.set_state('travel')
                    elif command in ['equip item', 'equip']:
                        if treasure_type == 'weapon':
                            game.get_player().inventory.equip_weapon(drop)
                            game.get_player().recalculate_stats()
                            input('\nPress enter to continue...')
                        elif treasure_type == 'armour':
                            slot = text.ArmourSlots[drop]
                            game.get_player().inventory.equip_armour(slot, drop)
                            game.get_player().recalculate_stats()
                            input('\nPress enter to continue...')

                        game.get_maze().current_room.drop = None
                        game.get_maze().current_room.claimed = True
                        game.set_state('travel')
                elif treasure_type == 'consumable':
                    game.get_player().inventory.add_item(drop)
                    print('You have obtained a ' + drop + '!')
                    game.set_state('consumable chest')
                    choices = game.get_options()
                    command = game.prompt_player_choice(choices).strip().lower()
                    if command.isdigit():
                        if int(command) > len(choices):
                            print(text.input_error_prompt)
                        else:
                            command = choices[int(command) - 1].strip().lower()
                    if command in ['go back', 'back']:
                        game.set_state('travel')
                    elif command in ['consume item', 'consume']:
                        if drop in text.Consumables:
                            if game.get_player().inventory.consume_item(drop):
                                if drop == 'Health potion':
                                    magnitude = game.get_player().stats.maxhealth * 0.1
                                    game.get_player().stats.maxhealth += magnitude
                                    print(f"Your max health has increased by {magnitude}!")
                                elif drop == 'Healing potion':
                                    magnitude = game.get_player().stats.maxhealth * 0.1
                                    game.get_player().stats.heal(magnitude)
                                    print(f'You have healed {magnitude} health!')
                                elif drop == 'Attack potion':
                                    magnitude = game.get_player().stats.attack * 0.1
                                    game.get_player().stats.attack += magnitude
                                    print(f'Your attack has increased by {magnitude}!')
                                input('\nPress enter to continue...')
                            else:
                                print(text.input_error_prompt)
                        else:
                            print(text.input_error_prompt)
                    game.get_maze().current_room.drop = None
                    game.get_maze().current_room.claimed = True
                    game.set_state('travel')
            
        elif command.startswith('fight'):
            os.system('clear')
            monster = mud.Monster(mud.Stats(text.Monsters[game.maze.current_room.monster][0], text.Monsters[game.maze.current_room.monster][1]))
            combat_seq = mud.CombatSequence(game.get_player(), monster, 3, 20)
            combat_seq.start_sequence()
        else:
            #print ABSTRACTED error message
            print(text.input_error_prompt)

        #print(text.printing_text_large_spacing)    

        #choices = game.get_options()
        #choice = mud.prompt_player_choice(choices)
        #actions = game.get_actions(choices, choice)
        #game.execute(actions)
        #data.display(game.status())
    #mud.epilogue()