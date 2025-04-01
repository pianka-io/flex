from time import sleep
from flex import *

ran = False

@loop(LoopType.FLEX)
def tick():
    global ran
    game = get_game()
    if game is None: return
    if not game.ready: return

    if ran:
        return
    ran = True
    list_items()

def list_items():
    for item in get_all_items():
        debug(f"Item: {item.type.name} (ID: {item.id})")
        if item.owner is None:
            debug(f"  No owner")
        else:
            debug(f"  Owner id: {item.owner.id}")
        debug(f"  Quality: {item.quality.name}")
        debug(f"  Level: {item.level}")
        debug(f"  Flags: {item.flags}")
        for stat in item.stats:
            debug(f"  Stat: {stat.type.name}, Value: {stat.value}")
