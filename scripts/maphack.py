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
        write_log("INF", "Revealing automap...")
        reveal_automap()
    last_game = game.name

@loop(LoopType.DRAW_AUTOMAP)
def draw_automap() -> list[Element]:
    game = get_game()
    if game is None: return []
    if not game.ready: return []
    player = get_player()

    elements = []

    elements.append(TextElement("me", TextColor.White, player.position))
    # elements.append(CrossElement(0, Position(100, 120)))

    return elements