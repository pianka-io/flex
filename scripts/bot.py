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
    # await pause(2000)
    if not Controls.create_game:
        return
    await Controls.create_game.click()

#####################################
## in game                         ##
#####################################
# path: Optional[list[Position]] = None
# @loop(LoopType.DRAW_AUTOMAP)
# def draw_automap() -> list[Element]:
#     global path
#     game = get_game()
#     if game is None: return []
#     if not game.ready: return []
#
#     elements = []
#
#     path_copy = list(path) if path else None
#     if path_copy and len(path_copy) > 1:
#         for i in range(len(path_copy) - 1):
#             elements.append(LineElement(path_copy[i], path_copy[i + 1], 0x5B))
#
#     return elements
#
# @loop(LoopType.CLIENT_STATE, ClientState.IN_GAME)
# async def when_in_game():
#     global path
#     game = get_game()
#     if game is None: return
#     if not game.ready: return
#
#     player = get_player()
#     if not player.level_data: return
#
#     akara_preset = find_akara_preset(player)
#     akara = find_akara()
#
#     if not akara:
#         path = find_room_path(player.position, akara_preset)
#     else:
#         path = find_room_path(player.position, akara.position)
#
# def find_akara_preset(player: Character) -> Optional[Position]:
#     akara_preset: Optional[Position] = None
#     for room in player.level_data.rooms:
#         for preset in room.presets:
#             if preset.preset_type == PresetType.MONSTER:
#                 if MonsterType(preset.type) == MonsterType.AKARA:
#                     akara_preset = preset.position
#                     break
#     return akara_preset
#
# def find_akara() -> Optional[Monster]:
#     akara: Optional[Monster] = None
#     for unit in get_nearby_units():
#         if isinstance(unit, Monster):
#             if unit.type == MonsterType.AKARA:
#                 akara = unit
#     return akara
