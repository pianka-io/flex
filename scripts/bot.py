import random

from flex import *

#####################################
## login                           ##
#####################################
run = False
@loop(LoopType.CLIENT_STATE, ClientState.NONE)
async def when_splash():
    global run
    if run:
        return
    run = True
    for _ in range(3):
        await mouse_click(MouseButton.LEFT, Position(0, 0))

@loop(LoopType.CLIENT_STATE, ClientState.MAIN_MENU)
async def when_main_menu():
    if not Controls.battle_net:
        return
    await Controls.battle_net.click()

@loop(LoopType.CLIENT_STATE, ClientState.LOGIN)
async def when_login():
    Controls.username.text = "flex"
    Controls.password.text = ""
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
    if not Controls.create:
        return
    await Controls.create.click()
    if not Controls.create_name:
        return
    Controls.create_name.text = "flex-" + str(random.randint(1, 1000))
    await pause(2000)
    if not Controls.create_game:
        return
    await Controls.create_game.click()

#####################################
## in game                         ##
#####################################
@loop(LoopType.CLIENT_STATE, ClientState.IN_GAME)
async def when_in_game():

    game = get_game()
    if game is None: return
    if not game.ready: return

    await pause(1000)
    # for preset in get_player().level_data.presets:
    #     if preset.preset_type == 1:
    #         info(str(MonsterType(preset.type).name))

    info("units")
    for unit in get_nearby_units():
        if isinstance(unit, Monster):
            info("  [MON] " + str(unit.type.name))
        # if isinstance(unit, Object):
        #     info("  [OBJ] " + str(unit.type.name))
        # el
        # if isinstance(unit, Item):
        #     info("  [ITM] " + str(unit.type.name))
        # else:
        #     info("  other")

    # path = find_level_path(LevelId.ROGUE_ENCAMPMENT, LevelId.CATACOMBS_LEVEL_4)
    # for step in path:
    #     print(str(step.name))
    #     level = Levels.find_level_by_id(step)
    #     if not level:
    #         continue
    #     for exit in level.exits:
    #         print("  " + str(exit))
    #         how_far = distance(get_player().position, exit.position)
    #         print("  distance: " + str(how_far))
