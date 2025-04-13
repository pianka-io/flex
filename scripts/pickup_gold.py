from flex import *

@loop(LoopType.FLEX)
async def tick():
    game = get_game()
    if game is None or not game.ready: return

    player = get_player()

    for item in get_all_items():
        if item.type == Miscellaneous.GOLD:
            how_far = distance(player.position, item.position)
            if how_far <= 5.0:
                pick_up(item)
