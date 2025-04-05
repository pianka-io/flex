import random

from flex import *

#####################################
## login                           ##
#####################################
@loop(LoopType.CLIENT_STATE, ClientState.NONE)
async def when_splash():
    for _ in range(3):
        await mouse_click(MouseButton.LEFT, Position(0, 0))

@loop(LoopType.CLIENT_STATE, ClientState.MAIN_MENU)
async def when_main_menu():
    await Controls.battle_net.click()

@loop(LoopType.CLIENT_STATE, ClientState.LOGIN)
async def when_login():
    Controls.username.text = "flex"
    Controls.password.text = "pianka"
    await Controls.log_in.click()

@loop(LoopType.CLIENT_STATE, ClientState.CHARACTER_SELECT)
async def when_character_select():
    for character in Controls.character_list:
        if character.text == "flex":
            await character.click()
            break
    await Controls.character_list_ok.click()

@loop(LoopType.CLIENT_STATE, ClientState.LOBBY)
@loop(LoopType.CLIENT_STATE, ClientState.CREATE)
async def when_lobby():
    if not Controls.create_name:
        await Controls.create.click()
    Controls.create_name.text = "flex-" + str(random.randint(1, 1000))
    await Controls.create_game.click()

#####################################
## in game                         ##
#####################################
@loop(LoopType.CLIENT_STATE, ClientState.IN_GAME)
async def when_in_game():
    info("in game")
