from flex import *

has_run: bool = False

@loop(LoopType.FLEX)
async def flex_loop():
    global has_run
    if has_run: return
    has_run = True

    await one_second()
    await opening_screen()
    await one_second()
    await battle_net()

async def one_second():
    await pause(1000)

async def opening_screen():
    await mouse_click(MouseButton.LEFT, Position(0, 0))
    await one_second()
    await mouse_click(MouseButton.LEFT, Position(0, 0))
    await one_second()
    await mouse_click(MouseButton.LEFT, Position(0, 0))

async def battle_net():
    button = Controls.battle_net()
    if button:
        await button.click()
