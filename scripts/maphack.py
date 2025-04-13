from flex import *

last_game: Optional[str] = None

@loop(LoopType.FLEX)
async def flex_loop():
    await ensure_revealed()

async def ensure_revealed():
    global last_game
    game = get_game()
    if game is None or not game.ready: return []

    if game.name != last_game:
        info("Revealing automap...")
        print_game(TextColor.Tan, "Revealing automap...")
        reveal_automap()
    last_game = game.name

@loop(LoopType.DRAW_AUTOMAP)
def draw_automap() -> list[Element]:
    game = get_game()
    if game is None or not game.ready: return []

    player = get_player()
    elements = []

    for monster in get_all_monsters():
        if monster.dead or monster.friendly or monster.dummy or len(monster.stats) == 0: continue
        cross = CrossElement(0x5B, monster.position)
        elements.append(cross)

    for item in get_all_items():
        if item.owner and item.owner.id != player.id and item.quality == Quality.UNIQUE:
            cross = CrossElement(0x97, item.position)
            elements.append(cross)

    return elements