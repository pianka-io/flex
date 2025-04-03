from flex import *


@loop(LoopType.FLEX)
async def flex_loop():
    await asyncio.sleep(10)
    for control in game.get_all_controls():
        info(str(control))
