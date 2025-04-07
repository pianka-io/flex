from flex import *

last_game: Optional[str] = None

@loop(LoopType.FLEX)
async def flex_loop():
    await ensure_revealed()

async def ensure_revealed():
    global last_game

    game = get_game()
    if game is None: return
    if not game.ready: return

    await pause(100)

    if game.name != last_game:
        info("Revealing automap...")
        print_game(TextColor.Tan, "Revealing automap...")
        reveal_automap()
    last_game = game.name

@loop(LoopType.DRAW_AUTOMAP)
def draw_automap() -> list[Element]:
    game = get_game()
    if game is None: return []
    if not game.ready: return []

    elements = []

    for monster in get_all_monsters():
        cross = CrossElement(0x5B, monster.position)
        elements.append(cross)

    return elements