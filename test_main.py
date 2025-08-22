import main

def test_main():
    main
    

test_main()
    
    



# For reference
# def test_main():
#     # 1. Start outside
#     assert main.player.location == "outside"
#     # 2. Go north
#     main.move("north")
#     # 3. Pick up a random item
#     room = main.get_room(player.location)
#     item_name = random.choice(room.get_items())
#     item = main.get_item(item_name)
#     main.player.add_item(item)
#     # 4. Check that item is in inventory
#     assert main.player.has_item(item_name)
#     # 5. Go east
#     main.move("east")
#     # 6. Check that we are in the hallway
#     assert main.player.location == "hallway"
#     # If any of the assertion conditions are False,
#     # Python will raise an AssertionError
