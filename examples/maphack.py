from flex import *

last_game: Optional[str] = None

@loop(LoopType.FLEX)
def flex_loop():
    ensure_revealed()

def ensure_revealed():
    global last_game

    game = get_game()
    if game is None: return
    if not game.ready: return

    if game.name != last_game:
        info("Revealing automap...")
        reveal_automap()
    last_game = game.name

# TODO: there's probably a better way to do this (from monstats.txt)
skip = [
    147, # gheed
    148, # akara
    150, # kashya
    152, # dummy
    154, # charsi
    155, # warriv
    179, # cow
    265, # cain
]

@loop(LoopType.DRAW_AUTOMAP)
def draw_automap() -> list[Element]:
    game = get_game()
    if game is None: return []
    if not game.ready: return []

    elements = []

    for monster in get_all_monsters():
        if monster.type in skip: continue
        cross = CrossElement(0x5B, monster.position)
        elements.append(cross)

    return elements