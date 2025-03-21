from flex import *

last_game: Optional[str] = None

@loop(LoopType.FLEX)
def tick():
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