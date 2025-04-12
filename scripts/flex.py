# ________/\\\\\__/\\\\\\_________________________________
#  ______/\\\///__\////\\\_________________________________
#   _____/\\\_________\/\\\_________________________________
#    __/\\\\\\\\\______\/\\\________/\\\\\\\\___/\\\____/\\\_
#     _\////\\\//_______\/\\\______/\\\/////\\\_\///\\\/\\\/__
#      ____\/\\\_________\/\\\_____/\\\\\\\\\\\____\///\\\/____
#       ____\/\\\_________\/\\\____\//\\///////______/\\\/\\\___
#        ____\/\\\_______/\\\\\\\\\__\//\\\\\\\\\\__/\\\/\///\\\_
#         ____\///_______\/////////____\//////////__\///____\///__

import traceback
from asyncio import AbstractEventLoop
from collections import defaultdict
from collections import deque
import game
import math
from typing import Optional, TypeAlias, Callable, Awaitable
from dataclasses import dataclass
from enum import IntEnum, StrEnum, Enum, auto
from game import wstring_at
from itertools import count
import asyncio
import inspect
import threading
import heapq

_asyncio_loop: AbstractEventLoop

def start_asyncio_loop():
    global _asyncio_loop
    loop = asyncio.new_event_loop()
    _asyncio_loop = loop  # Save reference
    asyncio.set_event_loop(loop)

    def run_loop():
        try:
            loop.run_forever()
        finally:
            loop.close()

    t = threading.Thread(target=run_loop, name="AsyncioLoop", daemon=True)
    t.start()
start_asyncio_loop()

#####################################
## general                         ##
#####################################
class NativePtr:
    def __init__(self, ptr: int):
        self._ptr = ptr

    @property
    def ptr(self) -> int:
        return self._ptr

@dataclass(frozen=True)
class Position:
    x: int
    y: int

@dataclass
class Dimensions:
    width: int
    height: int

class UnitType(IntEnum):
    PLAYER = 0
    MONSTER = 1
    OBJECT = 2
    MISSILE = 3
    ITEM = 4
    TILE = 5

class Unit:
    def __init__(self, unit: game.Unit):
        self._internal = unit

    @property
    def id(self) -> int:
        return self._internal.id

    @property
    def name(self) -> str:
        return game.get_unit_name(self._internal)

    @property
    def unit_type(self) -> UnitType:
        return UnitType(self._internal.type)

#####################################
## client                          ##
#####################################
class ClientState(Enum):
    NONE = auto()
    LOBBY = auto()
    INLINE = auto()
    CHAT = auto()
    MAIN_MENU = auto()
    LOGIN = auto()
    LOGIN_ERROR = auto()
    DISCONNECTED = auto()
    LOST_CONNECTION = auto()
    CONNECTING = auto()
    CHARACTER_SELECT = auto()
    CHARACTER_SELECT_NO_CHARS = auto()
    CHARACTER_SELECT_CHANGE_REALM = auto()
    CHARACTER_SELECT_PLEASE_WAIT = auto()
    CHARACTER_CREATE = auto()
    CHARACTER_CREATE_ALREADY_EXISTS = auto()
    NEW_CHARACTER = auto()
    NEW_ACCOUNT = auto()
    REALM_DOWN = auto()
    DIFFICULTY = auto()
    GAME_DOES_NOT_EXIST = auto()
    GAME_IS_FULL = auto()
    GAME_EXISTS = auto()
    SERVER_DOWN = auto()
    CREATE = auto()
    JOIN = auto()
    CHANNEL = auto()
    LADDER = auto()
    CDKEY_IN_USE = auto()
    UNABLE_TO_CONNECT = auto()
    INVALID_CDKEY = auto()
    SPLASH = auto()
    GATEWAY = auto()
    AGREE_TO_TERMS = auto()
    PLEASE_READ = auto()
    REGISTER_EMAIL = auto()
    CREDITS = auto()
    CINEMATICS = auto()
    OTHER_MULTIPLAYER = auto()
    ENTER_IP_ADDRESS = auto()
    TCP_IP = auto()
    PLEASE_WAIT = auto()
    IN_GAME = auto()

def get_client_state() -> ClientState:
    if game.is_game_ready():
        return ClientState.IN_GAME

    f = ControlsMeta._find_control

    # connecting to battle.net
    if f(Position(330, 416), Dimensions(128, 35)):
        return ClientState.CONNECTING

    # login error
    if f(Position(335, 412), Dimensions(128, 35)):
        return ClientState.LOGIN_ERROR

    # lost connection / disconnected / char create already exists
    if f(Position(351, 337), Dimensions(96, 32)):
        if f(Position(268, 320), Dimensions(264, 120)):
            return ClientState.LOST_CONNECTION  # checked first in C
        elif f(Position(268, 320), Dimensions(264, 120)):
            return ClientState.DISCONNECTED
        else:
            return ClientState.CHARACTER_CREATE_ALREADY_EXISTS

    # character select please wait / please wait
    if f(Position(351, 337), Dimensions(96, 32)):
        if f(Position(268, 300), Dimensions(264, 100)):
            return ClientState.CHARACTER_SELECT_PLEASE_WAIT
        elif f(Position(268, 320), Dimensions(264, 120)):
            return ClientState.PLEASE_WAIT

    # inline queue / create / join / channel / ladder
    if f(Position(433, 433), Dimensions(96, 32)):
        if f(Position(427, 234), Dimensions(300, 100)):
            return ClientState.INLINE
        elif f(Position(459, 380), Dimensions(150, 12)):
            return ClientState.CREATE
        elif f(Position(594, 433), Dimensions(172, 32)):
            return ClientState.JOIN
        elif f(Position(671, 433), Dimensions(96, 32)):
            return ClientState.CHANNEL
        else:
            return ClientState.LADDER

    # login / character select change realm / char select variants
    if f(Position(33, 572), Dimensions(128, 35)):
        if f(Position(264, 484), Dimensions(272, 35)):
            return ClientState.LOGIN
        elif f(Position(495, 438), Dimensions(96, 32)):
            return ClientState.CHARACTER_SELECT_CHANGE_REALM
        elif f(Position(627, 572), Dimensions(128, 35)) and f(Position(33, 528), Dimensions(168, 60)):
            if f(Position(264, 297), Dimensions(272, 35)):
                return ClientState.DIFFICULTY
            elif f(Position(37, 178), Dimensions(200, 92)):
                return ClientState.CHARACTER_SELECT
            elif f(Position(45, 318), Dimensions(531, 140)):
                return ClientState.REALM_DOWN
            else:
                return ClientState.CHARACTER_SELECT_NO_CHARS

        if f(Position(627, 572), Dimensions(128, 35)):
            return ClientState.CHARACTER_CREATE
        elif f(Position(321, 448), Dimensions(300, 32)):
            return ClientState.NEW_ACCOUNT
        else:
            return ClientState.NEW_CHARACTER

    # cd key / unable to connect / invalid cd key
    if f(Position(335, 450), Dimensions(128, 35)):
        if f(Position(162, 270), Dimensions(477, 50)):
            return ClientState.CDKEY_IN_USE
        elif f(Position(162, 420), Dimensions(477, 100)):
            return ClientState.UNABLE_TO_CONNECT
        else:
            return ClientState.INVALID_CDKEY

    # game does not exist / is full / exists / server down
    if f(Position(438, 300), Dimensions(326, 150)):
        return ClientState.GAME_DOES_NOT_EXIST  # all share same dimensions, prioritized
    if f(Position(438, 300), Dimensions(326, 150)):
        return ClientState.GAME_IS_FULL
    if f(Position(438, 300), Dimensions(326, 150)):
        return ClientState.GAME_EXISTS
    if f(Position(438, 300), Dimensions(326, 150)):
        return ClientState.SERVER_DOWN

    # main menu
    if f(Position(264, 324), Dimensions(272, 35)):
        return ClientState.MAIN_MENU

    # splash
    if f(Position(100, 580), Dimensions(600, 80)):
        return ClientState.SPLASH

    # lobby
    if f(Position(27, 480), Dimensions(120, 20)):
        return ClientState.LOBBY

    # chat
    if f(Position(187, 470), Dimensions(80, 20)):
        return ClientState.CHAT

    # gateway
    if f(Position(281, 538), Dimensions(96, 32)):
        return ClientState.GATEWAY

    # agree to terms
    if f(Position(525, 513), Dimensions(128, 35)):
        return ClientState.AGREE_TO_TERMS

    # please read
    if f(Position(525, 513), Dimensions(128, 35)):
        return ClientState.PLEASE_READ

    # register email
    if f(Position(265, 527), Dimensions(272, 35)):
        return ClientState.REGISTER_EMAIL

    # credits
    if f(Position(33, 578), Dimensions(128, 35)):
        return ClientState.CREDITS

    # cinematics
    if f(Position(334, 488), Dimensions(128, 35)):
        return ClientState.CINEMATICS

    # other multiplayer
    if f(Position(264, 350), Dimensions(272, 35)):
        return ClientState.OTHER_MULTIPLAYER

    # enter ip
    if f(Position(281, 337), Dimensions(96, 32)):
        return ClientState.ENTER_IP_ADDRESS

    # tcp/ip
    if f(Position(265, 206), Dimensions(272, 35)):
        return ClientState.TCP_IP

    return ClientState.NONE

#####################################
## controls                        ##
#####################################
class ControlType(IntEnum):
    EDIT_BOX = 0x01
    IMAGE = 0x02
    UNUSED = 0x03
    TEXT_BOX = 0x04
    SCROLL_BAR = 0x05
    BUTTON = 0x06
    LIST = 0x07
    TIMER = 0x08
    SMACK = 0x09
    PROGRESS_BAR = 0x0a
    POPUP = 0x0b
    ACCOUNT_LIST = 0x0c

class Control:
    def __init__(self, control: game.Control):
        self._internal_control = control

    @property
    def type(self) -> ControlType:
        return ControlType(self._internal_control.type)

    @property
    def position(self) -> Position:
        x = self._internal_control.x
        y = self._internal_control.y
        return Position(x, y)

    @property
    def dimensions(self) -> Dimensions:
        width = self._internal_control.size_x
        height = self._internal_control.size_y
        return Dimensions(width, height)

    @property
    def text(self) -> str:
        return self._internal_control.text

    @text.setter
    def text(self, value: str):
        game.set_control_text(self._internal_control, value)

    @property
    def items(self) -> list[str]:
        return self._internal_control.text_list

    async def click(self):
        x = self._internal_control.x
        y = self._internal_control.y
        width = self._internal_control.size_x
        height = self._internal_control.size_y
        click_x = int(x + (width / 2))
        click_y = int(y - (height / 2))
        await mouse_click(MouseButton.LEFT, Position(click_x, click_y))

class ControlsMeta:
    @staticmethod
    def _find_control(position: Position, dimensions: Dimensions) -> Optional[Control]:
        controls = get_all_controls()
        for control in controls:
            if control.position == position and control.dimensions == dimensions:
                return control
        return None

    ## main menu
    @property
    def single_player(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 324), Dimensions(272, 35))

    @property
    def battle_net(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 366), Dimensions(272, 35))

    @property
    def choose_gateway(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 391), Dimensions(272, 25))

    @property
    def gateway_list(cls) -> Optional[Control]:
        # to click the items: y = 344 + ((index * 24) + 12)
        return cls._find_control(Position(257, 500), Dimensions(292, 160))

    @property
    def gateway_list_ok(cls) -> Optional[Control]:
        return cls._find_control(Position(281, 538), Dimensions(96, 32))

    @property
    def other_multiplayer(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 433), Dimensions(272, 35))

    ## login screen
    @property
    def username(cls) -> Optional[Control]:
        return cls._find_control(Position(322, 342), Dimensions(162, 19))

    @property
    def password(cls) -> Optional[Control]:
        return cls._find_control(Position(322, 396), Dimensions(162, 19))

    @property
    def log_in(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 484), Dimensions(272, 35))

    @property
    def exit_login(cls) -> Optional[Control]:
        return cls._find_control(Position(264, 484), Dimensions(272, 35))

    ## character screen
    @property
    def character_list(cls) -> list[Control]:
        control = cls._find_control(Position(237, 178), Dimensions(72, 93))
        if control is None:
            return []
        raw_controls = game.get_character_controls(control._internal_control)
        return [Control(c) for c in raw_controls]

    @property
    def character_list_ok(cls) -> Optional[Control]:
        return cls._find_control(Position(627, 572), Dimensions(128, 35))

    ## lobby
    @property
    def enter_chat(cls) -> Optional[Control]:
        return cls._find_control(Position(27, 480), Dimensions(120, 20))

    @property
    def create(cls) -> Optional[Control]:
        return cls._find_control(Position(533, 469), Dimensions(120, 20))

    @property
    def join(cls) -> Optional[Control]:
        return cls._find_control(Position(652, 469), Dimensions(120, 20))

    ## create game
    @property
    def create_name(cls) -> Optional[Control]:
        return cls._find_control(Position(432, 162), Dimensions(158, 20))

    @property
    def create_password(cls) -> Optional[Control]:
        return cls._find_control(Position(432, 217), Dimensions(158, 20))

    @property
    def create_normal(cls) -> Optional[Control]:
        return cls._find_control(Position(430, 381), Dimensions(16, 16))

    @property
    def create_nightmare(cls) -> Optional[Control]:
        return cls._find_control(Position(555, 381), Dimensions(16, 16))

    @property
    def create_hell(cls) -> Optional[Control]:
        return cls._find_control(Position(698, 381), Dimensions(16, 16))

    @property
    def create_game(cls) -> Optional[Control]:
        return cls._find_control(Position(594, 433), Dimensions(172, 32))

    ## join game
    @property
    def join_name(cls) -> Optional[Control]:
        return cls._find_control(Position(432, 148), Dimensions(155, 20))

    @property
    def join_password(cls) -> Optional[Control]:
        return cls._find_control(Position(606, 148), Dimensions(158, 20))

    @property
    def join_game(cls) -> Optional[Control]:
        return cls._find_control(Position(594, 433), Dimensions(172, 32))

Controls = ControlsMeta()

class MouseButton(IntEnum):
    LEFT = 0
    RIGHT = 1

class ButtonDirection(IntEnum):
    UP = 0
    DOWN = 1

async def mouse_click(button: MouseButton, position: Position):
    game.mouse_click(position.x, position.y, int(button), ButtonDirection.DOWN)
    # await pause(100)
    game.mouse_click(position.x, position.y, int(button), ButtonDirection.UP)

#####################################
## game                            ##
#####################################
class Game:
    def __init__(self, game_info: game.GameInfo):
        self.__internal_game_info = game_info

    @property
    def ready(self) -> bool:
        return not not game.is_game_ready()

    @property
    def name(self) -> str:
        return self.__internal_game_info.name

#####################################
## map                             ##
#####################################
class MapTile:
    def __init__(self, internal, offset: Position):
        self._internal = internal
        self._offset = offset

    @property
    def position(self) -> Position:
        return Position(self._internal.level_x, self._internal.level_y)

    @property
    def walkable(self) -> bool:
        return not bool(self._internal.flags & 0x01) and not bool(self._internal.flags & 0x0002) and not bool(self._internal.flags & 0xffff)

    @property
    def occupied(self) -> bool:
        return bool(self._internal.flags & 0x08)

class PresetType(IntEnum):
    MONSTER = 1
    OBJECT = 2

class Preset:
    def __init__(self, internal: game.Preset):
        self._internal = internal

    @property
    def preset_type(self) -> PresetType:
        return PresetType(self._internal.type)

    @property
    def type(self) -> int:
        return self._internal.id

    @property
    def position(self) -> Position:
        return Position(self._internal.x, self._internal.y)

class MapRoom:
    def __init__(self, internal):
        self._internal = internal

    @property
    def presets(self) -> list[Preset]:
        presets = game.get_presets_for_room(self._internal)
        if presets is None:
            return []
        return [Preset(p) for p in presets if p.type in [1, 2]]

    @property
    def position(self) -> Position:
        return Position(self._internal.pos_x, self._internal.pos_y)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self._internal.size_x, self._internal.size_y)

    @property
    def center(self) -> Position:
        return Position(self.position.x + self.dimensions.width // 2,
                        self.position.y + self.dimensions.height // 2)

    @property
    def neighbors(self) -> list["MapRoom"]:
        return [MapRoom(r) for r in game.get_map_room_neighbors(self._internal)]

    @property
    def tiles(self) -> list[MapTile]:
        return [MapTile(t, self.position) for t in game.get_room_tiles(self._internal)]

class LevelId(IntEnum):
    NULL = 0
    ROGUE_ENCAMPMENT = 1
    BLOOD_MOOR = 2
    COLD_PLAINS = 3
    STONY_FIELD = 4
    DARK_WOOD = 5
    BLACK_MARSH = 6
    TAMOE_HIGHLAND = 7
    DEN_OF_EVIL = 8
    CAVE_LEVEL_1 = 9
    UNDERGROUND_PASSAGE_LEVEL_1 = 10
    HOLE_LEVEL_1 = 11
    PIT_LEVEL_1 = 12
    CAVE_LEVEL_2 = 13
    UNDERGROUND_PASSAGE_LEVEL_2 = 14
    HOLE_LEVEL_2 = 15
    PIT_LEVEL_2 = 16
    BURIAL_GROUNDS = 17
    CRYPT = 18
    MAUSOLEUM = 19
    FORGOTTEN_TOWER = 20
    TOWER_CELLAR_LEVEL_1 = 21
    TOWER_CELLAR_LEVEL_2 = 22
    TOWER_CELLAR_LEVEL_3 = 23
    TOWER_CELLAR_LEVEL_4 = 24
    TOWER_CELLAR_LEVEL_5 = 25
    MONASTERY_GATE = 26
    OUTER_CLOISTER = 27
    BARRACKS = 28
    JAIL_LEVEL_1 = 29
    JAIL_LEVEL_2 = 30
    JAIL_LEVEL_3 = 31
    INNER_CLOISTER = 32
    CATHEDRAL = 33
    CATACOMBS_LEVEL_1 = 34
    CATACOMBS_LEVEL_2 = 35
    CATACOMBS_LEVEL_3 = 36
    CATACOMBS_LEVEL_4 = 37
    TRISTRAM = 38
    MOO_MOO_FARM = 39
    LUT_GHOLEIN = 40
    ROCKY_WASTE = 41
    DRY_HILLS = 42
    FAR_OASIS = 43
    LOST_CITY = 44
    VALLEY_OF_SNAKES = 45
    CANYON_OF_THE_MAGI = 46
    SEWERS_LEVEL_1_ACT_2 = 47
    SEWERS_LEVEL_2_ACT_2 = 48
    SEWERS_LEVEL_3 = 49
    HAREM_LEVEL_1 = 50
    HAREM_LEVEL_2 = 51
    PALACE_CELLAR_LEVEL_1 = 52
    PALACE_CELLAR_LEVEL_2 = 53
    PALACE_CELLAR_LEVEL_3 = 54
    STONY_TOMB_LEVEL_1 = 55
    HALLS_OF_THE_DEAD_LEVEL_1 = 56
    HALLS_OF_THE_DEAD_LEVEL_2 = 57
    CLAW_VIPER_TEMPLE_LEVEL_1 = 58
    STONY_TOMB_LEVEL_2 = 59
    HALLS_OF_THE_DEAD_LEVEL_3 = 60
    CLAW_VIPER_TEMPLE_LEVEL_2 = 61
    MAGGOT_LAIR_LEVEL_1 = 62
    MAGGOT_LAIR_LEVEL_2 = 63
    MAGGOT_LAIR_LEVEL_3 = 64
    ANCIENT_TUNNELS = 65
    TAL_RASHAS_TOMB_1 = 66
    TAL_RASHAS_TOMB_2 = 67
    TAL_RASHAS_TOMB_3 = 68
    TAL_RASHAS_TOMB_4 = 69
    TAL_RASHAS_TOMB_5 = 70
    TAL_RASHAS_TOMB_6 = 71
    TAL_RASHAS_TOMB_7 = 72
    DURIELS_LAIR = 73
    ARCANE_SANCTUARY = 74
    KURAST_DOCKTOWN = 75
    SPIDER_FOREST = 76
    GREAT_MARSH = 77
    FLAYER_JUNGLE = 78
    LOWER_KURAST = 79
    KURAST_BAZAAR = 80
    UPPER_KURAST = 81
    KURAST_CAUSEWAY = 82
    TRAVINCAL = 83
    SPIDER_CAVE = 84
    SPIDER_CAVERN = 85
    SWAMPY_PIT_LEVEL_1 = 86
    SWAMPY_PIT_LEVEL_2 = 87
    FLAYER_DUNGEON_LEVEL_1 = 88
    FLAYER_DUNGEON_LEVEL_2 = 89
    SWAMPY_PIT_LEVEL_3 = 90
    FLAYER_DUNGEON_LEVEL_3 = 91
    SEWERS_LEVEL_1_ACT_3 = 92
    SEWERS_LEVEL_2_ACT_3 = 93
    RUINED_TEMPLE = 94
    DISUSED_FANE = 95
    FORGOTTEN_RELIQUARY = 96
    FORGOTTEN_TEMPLE = 97
    RUINED_FANE = 98
    DISUSED_RELIQUARY = 99
    DURANCE_OF_HATE_LEVEL_1 = 100
    DURANCE_OF_HATE_LEVEL_2 = 101
    DURANCE_OF_HATE_LEVEL_3 = 102
    PANDEMONIUM_FORTRESS = 103
    OUTER_STEPPES = 104
    PLAINS_OF_DESPAIR = 105
    CITY_OF_THE_DAMNED = 106
    RIVER_OF_FLAME = 107
    CHAOS_SANCTUM = 108
    HARROGATH = 109
    BLOODY_FOOTHILLS = 110
    RIGID_HIGHLANDS = 111
    ARREAT_PLATEAU = 112
    CRYSTALIZED_CAVERN_LEVEL_1 = 113
    CELLAR_OF_PITY = 114
    CRYSTALIZED_CAVERN_LEVEL_2 = 115
    ECHO_CHAMBER = 116
    TUNDRA_WASTELANDS = 117
    GLACIAL_CAVES_LEVEL_1 = 118
    GLACIAL_CAVES_LEVEL_2 = 119
    ROCKY_SUMMIT = 120
    NIHILATHAKS_TEMPLE = 121
    HALLS_OF_ANGUISH = 122
    HALLS_OF_DEATHS_CALLING = 123
    HALLS_OF_VAUGHT = 124
    HELL_1 = 125
    HELL_2 = 126
    HELL_3 = 127
    WORLDSTONE_KEEP_LEVEL_1 = 128
    WORLDSTONE_KEEP_LEVEL_2 = 129
    WORLDSTONE_KEEP_LEVEL_3 = 130
    THRONE_OF_DESTRUCTION = 131
    WORLDSTONE_CHAMBER = 132
    PANDEMONIUM_RUN_1 = 133
    PANDEMONIUM_RUN_2 = 134
    PANDEMONIUM_RUN_3 = 135
    PANDEMONIUM_TRISTRAM = 136
    WAYPOINT_JUMP = 9999

TownLevels = {
    LevelId.ROGUE_ENCAMPMENT,
    LevelId.LUT_GHOLEIN,
    LevelId.KURAST_DOCKTOWN,
    LevelId.PANDEMONIUM_FORTRESS,
    LevelId.HARROGATH
}

WaypointLevels = {
    LevelId.ROGUE_ENCAMPMENT,
    LevelId.COLD_PLAINS,
    LevelId.STONY_FIELD,
    LevelId.DARK_WOOD,
    LevelId.BLACK_MARSH,
    LevelId.OUTER_CLOISTER,
    LevelId.JAIL_LEVEL_1,
    LevelId.INNER_CLOISTER,
    LevelId.CATACOMBS_LEVEL_2,
    LevelId.LUT_GHOLEIN,
    LevelId.SEWERS_LEVEL_2_ACT_2,
    LevelId.DRY_HILLS,
    LevelId.HALLS_OF_THE_DEAD_LEVEL_2,
    LevelId.FAR_OASIS,
    LevelId.LOST_CITY,
    LevelId.PALACE_CELLAR_LEVEL_1,
    LevelId.ARCANE_SANCTUARY,
    LevelId.CANYON_OF_THE_MAGI,
    LevelId.KURAST_DOCKTOWN,
    LevelId.SPIDER_FOREST,
    LevelId.GREAT_MARSH,
    LevelId.FLAYER_JUNGLE,
    LevelId.LOWER_KURAST,
    LevelId.KURAST_BAZAAR,
    LevelId.UPPER_KURAST,
    LevelId.TRAVINCAL,
    LevelId.DURANCE_OF_HATE_LEVEL_2,
    LevelId.PANDEMONIUM_FORTRESS,
    LevelId.CITY_OF_THE_DAMNED,
    LevelId.RIVER_OF_FLAME,
    LevelId.HARROGATH,
    LevelId.RIGID_HIGHLANDS,
    LevelId.ARREAT_PLATEAU,
    LevelId.CRYSTALIZED_CAVERN_LEVEL_1,
    LevelId.CRYSTALIZED_CAVERN_LEVEL_2,
    LevelId.HALLS_OF_DEATHS_CALLING,
    LevelId.TUNDRA_WASTELANDS,
    LevelId.GLACIAL_CAVES_LEVEL_1,
    LevelId.WORLDSTONE_KEEP_LEVEL_2,
}

ReverseLevels: dict[LevelId, LevelId] = {
    LevelId(level): LevelId(parent)
    for level, parent in enumerate([
        0, 0, 1, 2, 3, 10, 5, 6, 2, 3, 4, 6, 7, 9, 10, 11, 12, 3, 17, 17, 6, 20, 21, 22, 23, 24,
        7, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 4, 1, 1, 40, 41, 42, 43, 44, 74, 40, 47,
        48, 40, 50, 51, 52, 53, 41, 42, 56, 45, 55, 57, 58, 43, 62, 63, 44, 46, 46, 46, 46, 46,
        46, 46, 1, 54, 1, 75, 76, 76, 78, 79, 80, 81, 82, 76, 76, 78, 86, 78, 88, 87, 89, 80,
        92, 80, 80, 81, 81, 82, 82, 83, 100, 101, 1, 103, 104, 105, 106, 107, 1, 109, 110, 111,
        112, 113, 113, 115, 115, 117, 118, 118, 109, 121, 122, 123, 111, 112, 117, 120, 128,
        129, 130, 131, 109, 109, 109, 109
    ])
}

ForwardLevels = defaultdict(list)

for child, parent in ReverseLevels.items():
    ForwardLevels[parent].append(child)

@dataclass
class LevelExit:
    from_level: LevelId
    to_level: LevelId
    position: Position

class MapLevel:
    def __init__(self, internal: game.Level):
        self._internal = internal

    @property
    def id(self) -> LevelId:
        return LevelId(self._internal.level_no)

    @property
    def position(self) -> Position:
        return Position(self._internal.pos_x, self._internal.pos_y)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self._internal.size_x, self._internal.size_y)

    @property
    def rooms(self) -> list[MapRoom]:
        return [MapRoom(r) for r in game.get_level_map_rooms(self._internal)]

    @property
    def exits(self) -> list[LevelExit]:
        raw_exits = game.get_level_exits(self._internal)
        return [
            LevelExit(
                from_level=LevelId(e["from"]),
                to_level=LevelId(e["to"]),
                position=Position(e["x"], e["y"])
            )
            for e in raw_exits or []
        ]

class Levels:
    @staticmethod
    def find_level_by_id(level_id: LevelId) -> Optional[MapLevel]:
        player = get_player()
        if not player:
            return None
        for level in game.get_act_levels(player.act_data._internal):
            if level.level_no == level_id:
                return MapLevel(level)
        return None

def find_level_path(from_level: LevelId, to_level: LevelId) -> list[LevelId] | None:
    queue = deque()
    visited = set()
    queue.append((from_level, [from_level], False))

    while queue:
        current, path, used_wp = queue.popleft()
        if current == to_level:
            return path
        if (current, used_wp) in visited:
            continue
        visited.add((current, used_wp))
        for child in ForwardLevels.get(current, []):
            if (child, used_wp) not in visited:
                queue.append((child, path + [child], used_wp))
        if not used_wp and current in WaypointLevels:
            for wp in WaypointLevels:
                if wp != current and (wp, True) not in visited:
                    queue.append((wp, path + [LevelId.WAYPOINT_JUMP, wp], True))

    return None

def nearest_walkable_tile(target: Position, tiles: list[MapTile]) -> Optional[Position]:
    return min(
        (t.position for t in tiles if t.walkable and not t.occupied),
        key=lambda p: abs(p.x - target.x) + abs(p.y - target.y),
        default=None
    )

def find_room_path(start: Position, end: Position) -> list[Position]:
    if start is None or end is None:
        error("start or end is None")
        return []

    player = get_player()
    tiles = [t for room in player.level_data.rooms for t in room.tiles]
    tile_map = {(t.position.x, t.position.y): t for t in tiles}

    def nearest_walkable(pos: Position) -> Optional[Position]:
        return min(
            (t.position for t in tiles if t.walkable and not t.occupied),
            key=lambda p: abs(p.x - pos.x) + abs(p.y - pos.y),
            default=None
        )

    if (start.x, start.y) not in tile_map or not tile_map[(start.x, start.y)].walkable:
        start = nearest_walkable(start)
    if (end.x, end.y) not in tile_map or not tile_map[(end.x, end.y)].walkable:
        end = nearest_walkable(end)

    if not start or not end:
        error("could not find valid start or end")
        return []

    def neighbors(pos: Position) -> list[Position]:
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = Position(pos.x + dx, pos.y + dy)
                t = tile_map.get((neighbor.x, neighbor.y))
                if t and t.walkable and not t.occupied:
                    out.append(neighbor)
        return out


    def heuristic(a: Position, b: Position) -> int:
        return abs(a.x - b.x) + abs(a.y - b.y)

    tie_breaker = count()
    open = [(0, next(tie_breaker), start)]
    came_from = {}
    cost = {start: 0}

    while open:
        _, __, current = heapq.heappop(open)

        if current == end:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for next_pos in neighbors(current):
            new_cost = cost[current] + 1
            if next_pos not in cost or new_cost < cost[next_pos]:
                cost[next_pos] = new_cost
                priority = new_cost + heuristic(next_pos, end)
                heapq.heappush(open, (priority, next(tie_breaker), next_pos))
                came_from[next_pos] = current

    return []

class ActData:
    def __init__(self, internal):
        self._internal: game.Act = internal

    @property
    def map_seed(self) -> int:
        return self._internal.dwMapSeed

    @property
    def levels(self) -> list[MapLevel]:
        levels = game.get_act_levels(self._internal)
        return [MapLevel(lvl) for lvl in levels] if levels else []

    @property
    def staff_tomb_level(self) -> int:
        return self._internal.pMisc.dwStaffTombLevel

#####################################
## movement                        ##
#####################################
async def walk_to(position: Position):
    ...

#####################################
## characters                      ##
#####################################
class Act(IntEnum):
    I = 0x00
    II = 0x01
    III = 0x02
    IV = 0x03
    V = 0x04

class Character(Unit):
    @property
    def position(self) -> Position:
        return Position(
            self._internal.pPathxPos,
            self._internal.pPathyPos
        )

    @property
    def in_town(self) -> bool:
        return self.level in TownLevels

    @property
    def act(self) -> Act:
        return Act(self._internal.dwAct)

    @property
    def act_data(self) -> Optional[ActData]:
        act_data = game.get_player_act(self._internal)
        return ActData(act_data) if act_data else None

    @property
    def level(self) -> LevelId:
        level = self.level_data
        return level.id if level else None

    @property
    def level_data(self) -> MapLevel:
        level = game.get_player_level(self._internal)
        return MapLevel(level)

    @property
    def map_room(self) -> Optional[MapRoom]:
        room = game.get_player_map_room(self._internal)
        return MapRoom(room) if room else None

class MonsterType(IntEnum):
    SKELETON = 0
    RETURNED = 1
    BONE_WARRIOR = 2
    BURNING_DEAD = 3
    HORROR = 4
    ZOMBIE = 5
    HUNGRY_DEAD = 6
    GHOUL = 7
    DROWNED_CARCASS = 8
    PLAGUE_BEARER = 9
    AFFLICTED = 10
    TAINTED = 11
    MISSHAPEN = 12
    DISFIGURED = 13
    DAMNED = 14
    FOUL_CROW = 15
    BLOOD_HAWK = 16
    BLACK_RAPTOR = 17
    CLOUD_STALKER = 18
    FALLEN = 19
    CARVER = 20
    DEVILKIN = 21
    DARK_ONE = 22
    WARPED_FALLEN = 23
    BRUTE = 24
    YETI = 25
    CRUSHER = 26
    WAILING_BEAST = 27
    GARGANTUAN_BEAST = 28
    SAND_RAIDER = 29
    MARAUDER = 30
    INVADER = 31
    INFIDEL = 32
    ASSAILANT = 33
    UNUSED_34 = 34
    UNUSED_35 = 35
    UNUSED_36 = 36
    UNUSED_37 = 37
    GHOST = 38
    WRAITH = 39
    SPECTER = 40
    APPARITION = 41
    DARK_SHAPE = 42
    DARK_HUNTER = 43
    VILE_HUNTER = 44
    DARK_STALKER = 45
    BLACK_ROGUE = 46
    FLESH_HUNTER = 47
    DUNE_BEAST = 48
    ROCK_DWELLER = 49
    JUNGLE_HUNTER = 50
    DOOM_APE = 51
    TEMPLE_GUARD = 52
    MOON_CLAN = 53
    NIGHT_CLAN = 54
    BLOOD_CLAN = 55
    HELL_CLAN = 56
    DEATH_CLAN = 57
    FALLEN_SHAMAN = 58
    CARVER_SHAMAN = 59
    DEVILKIN_SHAMAN = 60
    DARK_SHAMAN = 61
    WARPED_SHAMAN = 62
    QUILL_RAT = 63
    SPIKE_FIEND = 64
    THORN_BEAST = 65
    RAZOR_SPINE = 66
    JUNGLE_URCHIN = 67
    SAND_MAGGOT = 68
    ROCK_WORM = 69
    DEVOURER = 70
    GIANT_LAMPREY = 71
    WORLD_KILLER = 72
    TOMB_VIPER = 73
    CLAW_VIPER = 74
    SALAMANDER = 75
    PIT_VIPER = 76
    SERPENT_MAGUS = 77
    SAND_LEAPER = 78
    CAVE_LEAPER = 79
    TOMB_CREEPER = 80
    TREE_LURKER = 81
    RAZOR_PIT_DEMON = 82
    HUNTRESS = 83
    SABER_CAT = 84
    NIGHT_TIGER = 85
    HELL_CAT = 86
    ITCHIES = 87
    BLACK_LOCUSTS = 88
    PLAGUE_BUGS = 89
    HELL_SWARM = 90
    DUNG_SOLDIER = 91
    SAND_WARRIOR = 92
    SCARAB = 93
    STEEL_WEEVIL = 94
    ALBINO_ROACH = 95
    DRIED_CORPSE = 96
    DECAYED = 97
    EMBALMED = 98
    PRESERVED_DEAD = 99
    CADAVER = 100
    HOLLOW_ONE = 101
    GUARDIAN = 102
    UNRAVELER = 103
    HORADRIM_ANCIENT = 104
    BAAL_SUBJECT_MUMMY = 105
    UNUSED_106 = 106
    UNUSED_107 = 107
    UNUSED_108 = 108
    UNUSED_109 = 109
    CARRION_BIRD = 110
    UNDEAD_SCAVENGER = 111
    HELL_BUZZARD = 112
    WINGED_NIGHTMARE = 113
    SUCKER = 114
    FEEDER = 115
    BLOOD_HOOK = 116
    BLOOD_WING = 117
    GLOAM = 118
    SWAMP_GHOST = 119
    BURNING_SOUL = 120
    BLACK_SOUL = 121
    ARACH = 122
    SAND_FISHER = 123
    POISON_SPINNER = 124
    FLAME_SPIDER = 125
    SPIDER_MAGUS = 126
    THORNED_HULK = 127
    BRAMBLE_HULK = 128
    THRASHER = 129
    SPIKEFIST = 130
    GHOUL_LORD = 131
    NIGHT_LORD = 132
    DARK_LORD = 133
    BLOOD_LORD = 134
    BANISHED = 135
    DESERT_WING = 136
    FIEND = 137
    GLOOMBAT = 138
    BLOOD_DIVER = 139
    DARK_FAMILIAR = 140
    RAT_MAN = 141
    FETISH = 142
    FLAYER = 143
    SOUL_KILLER = 144
    STYGIAN_DOLL = 145
    DECKARD_CAIN_146 = 146
    GHEED = 147
    AKARA = 148
    CHICKEN = 149
    KASHYA = 150
    RAT = 151
    ROGUE = 152
    HELL_METEOR = 153
    CHARSI = 154
    WARRIV = 155
    ANDARIEL = 156
    BIRD_ONE = 157
    BIRD_TWO = 158
    BAT = 159
    DARK_RANGER = 160
    VILE_ARCHER = 161
    DARK_ARCHER = 162
    BLACK_ARCHER = 163
    FLESH_ARCHER = 164
    DARK_SPEARWOMAN = 165
    VILE_LANCER = 166
    DARK_LANCER = 167
    BLACK_LANCER = 168
    FLESH_LANCER = 169
    SKELETON_ARCHER = 170
    RETURNED_ARCHER = 171
    BONE_ARCHER = 172
    BURNING_DEAD_ARCHER = 173
    HORROR_ARCHER = 174
    WARRIV_2 = 175
    ATMA = 176
    DROGNAN = 177
    FARA = 178
    COW = 179
    SAND_MAGGOT_YOUNG = 180
    ROCK_WORM_YOUNG = 181
    DEVOURER_YOUNG = 182
    GIANT_LAMPREY_YOUNG = 183
    WORLD_KILLER_YOUNG = 184
    CAMEL = 185
    BLUNDERBORE = 186
    GORBELLY = 187
    MAULER = 188
    URDAR = 189
    SAND_MAGGOT_EGG = 190
    ROCK_WORM_EGG = 191
    DEVOURER_EGG = 192
    GIANT_LAMPREY_EGG = 193
    WORLD_KILLER_EGG = 194
    ACT_2_MAN = 195
    ACT_2_WOMAN = 196
    ACT_2_CHILD = 197
    GREIZ = 198
    ELZIX = 199
    GEGLASH = 200
    JERHYN = 201
    LYSANDER = 202
    ACT_2_GUARD = 203
    ACT_2_VENDOR_ONE = 204
    ACT_2_VENDOR_TWO = 205
    FOUL_CROW_NEST = 206
    BLOOD_HAWK_NEST = 207
    BLACK_VULTURE_NEST = 208
    CLOUD_STALKER_NEST = 209
    MESHIF = 210
    DURIEL = 211
    UNDEAD_RAT_MAN = 212
    UNDEAD_FETISH = 213
    UNDEAD_FLAYER = 214
    UNDEAD_SOUL_KILLER = 215
    UNDEAD_STYGIAN_DOLL = 216
    UNUSED_217 = 217
    UNUSED_218 = 218
    UNUSED_219 = 219
    UNUSED_220 = 220
    UNUSED_221 = 221
    UNUSED_222 = 222
    UNUSED_223 = 223
    UNUSED_224 = 224
    UNUSED_225 = 225
    UNUSED_226 = 226
    MAGGOT = 227
    MUMMY_GENERATOR = 228
    RADAMENT = 229
    UNUSED_230 = 230
    UNUSED_231 = 231
    UNUSED_232 = 232
    UNUSED_233 = 233
    FLYING_SCIMITAR = 234
    ZAKARUMITE = 235
    FAITHFUL = 236
    ZEALOT = 237
    SEXTON = 238
    CANTOR = 239
    HEIROPHANT_240 = 240
    HEIROPHANT_241 = 241
    MEPHISTO = 242
    DIABLO = 243
    DECKARD_CAIN_244 = 244
    DECKARD_CAIN_245 = 245
    DECKARD_CAIN_246 = 246
    SWAMP_DWELLER = 247
    BOG_CREATURE = 248
    SLIME_PRINCE = 249
    SUMMONER = 250
    TYRAEL = 251
    ASHEARA = 252
    HRATLI = 253
    ALKOR = 254
    ORMUS = 255
    IZUAL = 256
    HALBU = 257
    WATER_WATCHER_LIMB = 258
    RIVER_STALKER_LIMB = 259
    STYGIAN_WATCHER_LIMB = 260
    WATER_WATCHER_HEAD = 261
    RIVER_STALKER_HEAD = 262
    STYGIAN_WATCHER_HEAD = 263
    MESHIF_264 = 264
    DECKARD_CAIN_265 = 265
    NAVI = 266
    BLOODRAVEN = 267
    BUG = 268
    SCORPION = 269
    ROGUE_SCOUT = 270
    ROGUE_HIRE = 271
    ROGUE_OTHER = 272
    GARGOYLE_TRAP = 273
    RETURNED_MAGE = 274
    BONE_MAGE = 275
    BURNING_DEAD_MAGE = 276
    HORROR_MAGE = 277
    RAT_MAN_SHAMAN = 278
    FETISH_SHAMAN = 279
    FLAYER_SHAMAN = 280
    SOUL_KILLER_SHAMAN = 281
    STYGIAN_DOLL_SHAMAN = 282
    LARVA = 283
    SAND_MAGGOT_QUEEN = 284
    ROCK_WORM_QUEEN = 285
    DEVOURER_QUEEN = 286
    GIANT_LAMPREY_QUEEN = 287
    WORLD_KILLER_QUEEN = 288
    CLAY_GOLEM = 289
    BLOOD_GOLEM = 290
    IRON_GOLEM = 291
    FIRE_GOLEM = 292
    FAMILIAR = 293
    ACT_3_MAN = 294
    NIGHT_MARAUDER = 295
    ACT_3_WOMAN = 296
    NATALYA = 297
    FLESH_SPAWNER = 298
    STYGIAN_HAG = 299
    GROTESQUE = 300
    VILE_CHILD_1 = 301
    VILE_CHILD_2 = 302
    VILE_CHILD_3 = 303
    FINGER_MAGE_1 = 304
    FINGER_MAGE_2 = 305
    FINGER_MAGE_3 = 306
    REGURGITATOR_1 = 307
    REGURGITATOR_2 = 308
    REGURGITATOR_3 = 309
    DOOM_KNIGHT_1 = 310
    DOOM_KNIGHT_2 = 311
    DOOM_KNIGHT_3 = 312
    QUILL_BEAR_1 = 313
    QUILL_BEAR_2 = 314
    QUILL_BEAR_3 = 315
    QUILL_BEAR_4 = 316
    QUILL_BEAR_5 = 317
    SNAKE = 318
    PARROT = 319
    FISH = 320
    EVIL_HOLE_1 = 321
    EVIL_HOLE_2 = 322
    EVIL_HOLE_3 = 323
    EVIL_HOLE_4 = 324
    EVIL_HOLE_5 = 325
    TRAP_FIREBOLT = 326
    TRAP_HORZ_MISSILE = 327
    TRAP_VERT_MISSILE = 328
    TRAP_POISON_CLOUD = 329
    TRAP_LIGHTNING = 330
    ACT2_GUARD_2 = 331
    INVISO_SPAWNER = 332
    DIABLO_CLONE = 333
    SUCKER_NEST_1 = 334
    SUCKER_NEST_2 = 335
    SUCKER_NEST_3 = 336
    SUCKER_NEST_4 = 337
    ACT2_HIRE = 338
    MINI_SPIDER = 339
    BONE_PRISON_1 = 340
    BONE_PRISON_2 = 341
    BONE_PRISON_3 = 342
    BONE_PRISON_4 = 343
    BONE_WALL = 344
    COUNCIL_MEMBER_1 = 345
    COUNCIL_MEMBER_2 = 346
    COUNCIL_MEMBER_3 = 347
    TURRET_1 = 348
    TURRET_2 = 349
    TURRET_3 = 350
    HYDRA_1 = 351
    HYDRA_2 = 352
    HYDRA_3 = 353
    TRAP_MELEE = 354
    SEVEN_TOMBS = 355
    DOPPLEZON = 356
    VALKYRIE = 357
    ACT2_GUARD_3 = 358
    ACT3_HIRE = 359
    MEGA_DEMON_1 = 360
    MEGA_DEMON_2 = 361
    MEGA_DEMON_3 = 362
    NECRO_SKELETON = 363
    NECRO_MAGE = 364
    GRISWOLD = 365
    COMPELLING_ORB = 366
    TYRAEL_2 = 367
    DARK_WANDERER = 368
    TRAP_NOVA = 369
    SPIRIT_MUMMY = 370
    LIGHTNING_SPIRE = 371
    FIRE_TOWER = 372
    SLINGER_1 = 373
    SLINGER_2 = 374
    SLINGER_3 = 375
    SLINGER_4 = 376
    ACT2_GUARD_4 = 377
    ACT2_GUARD_5 = 378
    SKMAGE_COLD_1 = 379
    SKMAGE_COLD_2 = 380
    SKMAGE_COLD_3 = 381
    SKMAGE_COLD_4 = 382
    SKMAGE_FIRE_1 = 383
    SKMAGE_FIRE_2 = 384
    SKMAGE_FIRE_3 = 385
    SKMAGE_FIRE_4 = 386
    SKMAGE_LTNG_1 = 387
    SKMAGE_LTNG_2 = 388
    SKMAGE_LTNG_3 = 389
    SKMAGE_LTNG_4 = 390
    HELL_BOVINE = 391
    WINDOW_1 = 392
    WINDOW_2 = 393
    SLINGER_5 = 394
    SLINGER_6 = 395
    FETISH_BLOW_1 = 396
    FETISH_BLOW_2 = 397
    FETISH_BLOW_3 = 398
    FETISH_BLOW_4 = 399
    FETISH_BLOW_5 = 400
    MEPHISTO_SPIRIT = 401
    THE_SMITH = 402
    TRAPPED_SOUL_403 = 403
    TRAPPED_SOUL_404 = 404
    JAMELLA = 405
    IZUAL_406 = 406
    RAT_MAN_407 = 407
    MALACHAI = 408
    THE_FEATURE_CREEP = 409
    WAKE_OF_DESTRUCTION = 410
    CHARGED_BOLT_SENTRY = 411
    LIGHTNING_SENTRY = 412
    BLADE_CREEPER = 413
    INVIS_PET = 414
    INFERNO_SENTRY = 415
    DEATH_SENTRY = 416
    SHADOW_WARRIOR = 417
    SHADOW_MASTER = 418
    DRUID_HAWK = 419
    DRUID_SPIRIT_WOLF = 420
    DRUID_FENRIS = 421
    SPIRIT_OF_BARBS = 422
    HEART_OF_WOLVERINE = 423
    OAK_SAGE = 424
    DRUID_PLAGUE_POPPY = 425
    DRUID_CYCLE_OF_LIFE = 426
    VINE_CREATURE = 427
    DRUID_BEAR = 428
    EAGLE = 429
    WOLF = 430
    BEAR = 431
    BARRICADE_DOOR_432 = 432
    BARRICADE_DOOR_433 = 433
    PRISON_DOOR = 434
    BARRICADE_TOWER = 435
    ROT_WALKER = 436
    REANIMATED_HORDE = 437
    PROWLING_DEAD = 438
    UNHOLY_CORPSE = 439
    DEFILED_WARRIOR = 440
    SIEGE_BEAST = 441
    CRUSH_BIEST = 442
    BLOOD_BRINGER = 443
    GORE_BEARER = 444
    DEAMON_STEED = 445
    SNOW_YETI_1 = 446
    SNOW_YETI_2 = 447
    SNOW_YETI_3 = 448
    SNOW_YETI_4 = 449
    WOLF_RIDER_1 = 450
    WOLF_RIDER_2 = 451
    WOLF_RIDER_3 = 452
    MINIONEXP = 453
    SLAYEREXP = 454
    ICE_BOAR = 455
    FIRE_BOAR = 456
    HELL_SPAWN = 457
    ICE_SPAWN = 458
    GREATER_HELL_SPAWN = 459
    GREATER_ICE_SPAWN = 460
    FANATIC_MINION = 461
    BERSERK_SLAYER = 462
    CONSUMED_ICE_BOAR = 463
    CONSUMED_FIRE_BOAR = 464
    FRENZIED_HELL_SPAWN = 465
    FRENZIED_ICE_SPAWN = 466
    INSANE_HELL_SPAWN = 467
    INSANE_ICE_SPAWN = 468
    SUCCUBUSEXP = 469
    VILE_TEMPTRESS = 470
    STYGIAN_HARLOT = 471
    HELL_TEMPTRESS = 472
    BLOOD_TEMPTRESS = 473
    DOMINUS = 474
    VILE_WITCH = 475
    STYGIAN_FURY = 476
    BLOOD_WITCH = 477
    HELL_WITCH = 478
    OVER_SEER = 479
    LASHER = 480
    OVER_LORD = 481
    BLOOD_BOSS = 482
    HELL_WHIP = 483
    MINION_SPAWNER = 484
    MINION_SLAYER_SPAWNER = 485
    MINION_ICE_FIRE_BOAR_SPAWNER_486 = 486
    MINION_ICE_FIRE_BOAR_SPAWNER_487 = 487
    MINION_ICE_HELL_SPAWN_SPAWNER_488 = 488
    MINION_ICE_FIRE_BOAR_SPAWNER_489 = 489
    MINION_ICE_FIRE_BOAR_SPAWNER_490 = 490
    MINION_ICE_HELL_SPAWN_SPAWNER_491 = 491
    IMP_1 = 492
    IMP_2 = 493
    IMP_3 = 494
    IMP_4 = 495
    IMP_5 = 496
    CATAPULT_S = 497
    CATAPULT_E = 498
    CATAPULT_SIEGE = 499
    CATAPULT_W = 500
    FROZEN_HORROR_1 = 501
    FROZEN_HORROR_2 = 502
    FROZEN_HORROR_3 = 503
    FROZEN_HORROR_4 = 504
    FROZEN_HORROR_5 = 505
    BLOOD_LORD_1 = 506
    BLOOD_LORD_2 = 507
    BLOOD_LORD_3 = 508
    BLOOD_LORD_4 = 509
    BLOOD_LORD_5 = 510
    LARZUK = 511
    DREHYA_512 = 512
    MALAH = 513
    NIHLATHAK_TOWN = 514
    QUAL_KEHK = 515
    CATAPULT_SPOTTER_S = 516
    CATAPULT_SPOTTER_E = 517
    CATAPULT_SPOTTER_SIEGE = 518
    CATAPULT_SPOTTER_W = 519
    DECKARD_CAIN_520 = 520
    TYRAEL_521 = 521
    ACT_5_COMBATANT_1 = 522
    ACT_5_COMBATANT_2 = 523
    BARRICADE_WALL_RIGHT = 524
    BARRICADE_WALL_LEFT = 525
    NIHLATHAK = 526
    DREHYA_527 = 527
    EVIL_HUT = 528
    DEATH_MAULER_1 = 529
    DEATH_MAULER_2 = 530
    DEATH_MAULER_3 = 531
    DEATH_MAULER_4 = 532
    DEATH_MAULER_5 = 533
    POW = 534
    ACT_5_TOWNGUARD_1 = 535
    ACT_5_TOWNGUARD_2 = 536
    ANCIENT_STATUE_1 = 537
    ANCIENT_STATUE_2 = 538
    ANCIENT_STATUE_3 = 539
    ANCIENT_BARBARIAN_1 = 540
    ANCIENT_BARBARIAN_2 = 541
    ANCIENT_BARBARIAN_3 = 542
    BAAL_THRONE = 543
    BAAL_CRAB = 544
    BAAL_TAUNT = 545
    PUTRID_DEFILER_1 = 546
    PUTRID_DEFILER_2 = 547
    PUTRID_DEFILER_3 = 548
    PUTRID_DEFILER_4 = 549
    PUTRID_DEFILER_5 = 550
    PAIN_WORM_1 = 551
    PAIN_WORM_2 = 552
    PAIN_WORM_3 = 553
    PAIN_WORM_4 = 554
    PAIN_WORM_5 = 555
    BUNNY = 556
    COUNCIL_MEMBER_557 = 557
    VENOM_LORD_558 = 558
    BAAL_CRAB_TO_STAIRS = 559
    ACT_5_HIRELING_1HS = 560
    ACT_5_HIRELING_2HS = 561
    BAAL_TENTACLE_1 = 562
    BAAL_TENTACLE_2 = 563
    BAAL_TENTACLE_3 = 564
    BAAL_TENTACLE_4 = 565
    BAAL_TENTACLE_5 = 566
    INJURED_BARBARIAN_1 = 567
    INJURED_BARBARIAN_2 = 568
    INJURED_BARBARIAN_3 = 569
    BAAL_CRAB_CLONE = 570
    BAALS_MINION_1 = 571
    BAALS_MINION_2 = 572
    BAALS_MINION_3 = 573
    WORLDSTONE_EFFECT = 574
    BURNING_DEAD_ARCHER_575 = 575
    BONE_ARCHER_576 = 576
    BURNING_DEAD_ARCHER_577 = 577
    RETURNED_ARCHER_578 = 578
    HORROR_ARCHER_579 = 579
    AFFLICTED_580 = 580
    TAINTED_581 = 581
    MISSHAPEN_582 = 582
    DISFIGURED_583 = 583
    DAMNED_584 = 584
    MOON_CLAN_585 = 585
    NIGHT_CLAN_586 = 586
    HELL_CLAN_587 = 587
    BLOOD_CLAN_588 = 588
    DEATH_CLAN_589 = 589
    FOUL_CROW_590 = 590
    BLOOD_HAWK_591 = 591
    BLACK_RAPTOR_592 = 592
    CLOUD_STALKER_593 = 593
    CLAW_VIPER_594 = 594
    PIT_VIPER_595 = 595
    SALAMANDER_596 = 596
    TOMB_VIPER_597 = 597
    SERPENT_MAGUS_598 = 598
    MARAUDER_599 = 599
    INFIDEL_600 = 600
    SAND_RAIDER_601 = 601
    INVADER_602 = 602
    ASSAILANT_603 = 603
    DEATH_MAULER_604 = 604
    QUILL_RAT_605 = 605
    SPIKE_FIEND_606 = 606
    RAZOR_SPINE_607 = 607
    CARRION_BIRD_608 = 608
    THORNED_HULK_609 = 609
    SLINGER_610 = 610
    SLINGER_611 = 611
    SLINGER_612 = 612
    VILE_ARCHER_613 = 613
    DARK_ARCHER_614 = 614
    VILE_LANCER_615 = 615
    DARK_LANCER_616 = 616
    BLACK_LANCER_617 = 617
    BLUNDERBORE_618 = 618
    MAULER_619 = 619
    RETURNED_MAGE_620 = 620
    BURNING_DEAD_MAGE_621 = 621
    RETURNED_MAGE_622 = 622
    HORROR_MAGE_623 = 623
    BONE_MAGE_624 = 624
    HORROR_MAGE_625 = 625
    HORROR_MAGE_626 = 626
    HUNTRESS_627 = 627
    SABER_CAT_628 = 628
    CAVE_LEAPER_629 = 629
    TOMB_CREEPER_630 = 630
    GHOST_631 = 631
    WRAITH_632 = 632
    SPECTER_633 = 633
    SUCCUBUSEXP_634 = 634
    HELL_TEMPTRESS_635 = 635
    DOMINUS_636 = 636
    HELL_WITCH_637 = 637
    VILE_WITCH_638 = 638
    GLOAM_639 = 639
    BLACK_SOUL_640 = 640
    BURNING_SOUL_641 = 641
    CARVER_642 = 642
    DEVILKIN_643 = 643
    DARK_ONE_644 = 644
    CARVER_SHAMAN_645 = 645
    DEVILKIN_SHAMAN_646 = 646
    DARK_SHAMAN_647 = 647
    BONE_WARRIOR_648 = 648
    RETURNED_649 = 649
    GLOOMBAT_650 = 650
    FIEND_651 = 651
    BLOOD_LORD_652 = 652
    BLOOD_LORD_654 = 653
    SCARAB_654 = 654
    STEEL_WEEVIL_655 = 655
    FLAYER_656 = 656
    STYGIAN_DOLL_657 = 657
    SOUL_KILLER_658 = 658
    FLAYER_659 = 659
    STYGIAN_DOLL_660 = 660
    SOUL_KILLER_661 = 661
    FLAYER_SHAMAN_662 = 662
    STYGIAN_DOLL_SHAMAN_663 = 663
    SOUL_KILLER_SHAMAN_664 = 664
    TEMPLE_GUARD_665 = 665
    TEMPLE_GUARD_666 = 666
    GUARDIAN_667 = 667
    UNRAVELER_668 = 668
    HORADRIM_ANCIENT_669 = 669
    HORADRIM_ANCIENT_670 = 670
    ZEALOT_671 = 671
    ZEALOT_672 = 672
    HEIROPHANT_673 = 673
    HEIROPHANT_674 = 674
    GROTESQUE_675 = 675
    FLESH_SPAWNER_676 = 676
    GROTESQUE_WYRM_677 = 677
    FLESH_BEAST_678 = 678
    WORLD_KILLER_679 = 679
    WORLD_KILLER_YOUNG_680 = 680
    WORLD_KILLER_EGG_681 = 681
    SLAYEREXP_682 = 682
    HELL_SPAWN_683 = 683
    GREATER_HELL_SPAWN_684 = 684
    ARACH_685 = 685
    BALROG_686 = 686
    PIT_LORD_687 = 687
    IMP_1_688 = 688
    IMP_4_689 = 689
    UNDEAD_STYGIAN_DOLL_690 = 690
    UNDEAD_SOUL_KILLER_691 = 691
    STRANGLER_692 = 692
    STORM_CASTER_693 = 693
    MAW_FIEND_694 = 694
    BLOOD_LORD_695 = 695
    GHOUL_LORD_696 = 696
    DARK_LORD_697 = 697
    UNHOLY_CORPSE_698 = 698
    DOOM_KNIGHT_699 = 699
    DOOM_KNIGHT_700 = 700
    OBLIVION_KNIGHT_701 = 701
    OBLIVION_KNIGHT_702 = 702
    CADAVER_703 = 703
    MEPHISTO_704 = 704
    DIABLO_705 = 705
    IZUAL_706 = 706
    LILITH_707 = 707
    DURIEL_708 = 708
    BAAL_CRAB_709 = 709
    EVIL_HUT_710 = 710
    DEMON_HOLE = 711
    PIT_LORD_712 = 712
    OBLIVION_KNIGHT_713 = 713
    IMP_4_714 = 714
    HELL_SWARM_715 = 715
    WORLD_KILLER_716 = 716
    ARACH_717 = 717
    STEEL_WEEVIL_718 = 718
    HELL_TEMPTRESS_719 = 719
    VILE_WITCH_720 = 720
    FLESH_HUNTER_721 = 721
    DARK_ARCHER_722 = 722
    BLACK_LANCER_723 = 723
    HELL_WHIP_724 = 724
    RETURNED_725 = 725
    HORROR_ARCHER_726 = 726
    BURNING_DEAD_MAGE_727 = 727
    HORROR_MAGE_728 = 728
    BONE_MAGE_729 = 729
    HORROR_MAGE_730 = 730
    DARK_LORD_731 = 731
    SPECTER_732 = 732
    BURNING_SOUL_733 = 733

@dataclass
class MonsterTier:
    normal: bool
    minion: bool
    champion: bool
    boss: bool

class Monster(Unit):
    @property
    def name(self) -> str:
        addr = self._internal.pMonsterDatawName
        if not addr:
            return ""
        return wstring_at(addr)

    @property
    def type(self) -> MonsterType:
        return MonsterType(self._internal.dwTxtFileNo)

    @property
    def mode(self) -> int:
        return self._internal.dwMode

    @property
    def position(self) -> Position:
        return Position(
            self._internal.pPathxPos,
            self._internal.pPathyPos
        )

    @property
    def tier(self) -> MonsterTier:
        return MonsterTier(
            normal = self._internal.pMonsterDatafNormal,
            minion = self._internal.pMonsterDatafMinion,
            champion = self._internal.pMonsterDatafChamp,
            boss =  self._internal.pMonsterDatafBoss
        )

#####################################
## objects                         ##
#####################################
class ObjectType(IntEnum):
    UNKNOWN = -1
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

    DUMMY_0 = 0
    CASKET_1 = 1
    SHRINE_2 = 2
    CASKET_3 = 3
    LARGE_URN_4 = 4
    CHEST_5 = 5
    CHEST_6 = 6
    BARREL_7 = 7
    TOWER_TOME_8 = 8
    URN_9 = 9
    BENCH = 10
    BARREL_11 = 11
    ROGUE_FOUNTAIN = 12
    DOOR_13 = 13
    DOOR_14 = 14
    DOOR_15 = 15
    DOOR_16 = 16
    STONE_ALPHA_17 = 17
    STONE_BETA_18 = 18
    STONE_GAMMA_19 = 19
    STONE_DELTA_20 = 20
    STONE_LAMBDA_21 = 21
    STONE_THETA_22 = 22
    DOOR_23 = 23
    DOOR_24 = 24
    DOOR_25 = 25
    GIBBET_26 = 26
    DOOR_27 = 27
    HOLE_ANIM_28 = 28
    BRAZIER = 29
    INIFUSS_30 = 30
    FOUNTAIN = 31
    CRUCIFIX = 32
    CANDLES_ONE = 33
    CANDLES_TWO = 34
    STANDARD_ONE = 35
    STANDARD_TWO = 36
    TIKI_TORCH = 37
    DUMMY_38 = 38
    FIRE_39 = 39
    DUMMY_40 = 40
    DUMMY_41 = 41
    DUMMY_42 = 42
    DUMMY_43 = 43
    DUMMY_44 = 44
    AMBIENT_SOUND_45 = 45
    CRATE_46 = 46
    DOOR_47 = 47
    DUMMY_48 = 48
    DUMMY_49 = 49
    CASKET_50 = 50
    CASKET_51 = 51
    URN_52 = 52
    CASKET_53 = 53
    ROGUE_CORPSE_54 = 54
    ROGUE_CORPSE_55 = 55
    ROGUE_CORPSE_56 = 56
    CORPSE_ON_STICK_57 = 57
    CORPSE_ON_STICK_58 = 58
    PORTAL_59 = 59
    PORTAL_60 = 60
    DUMMY_61 = 61
    DOOR_62 = 62
    DOOR_63 = 63
    DOOR_64 = 64
    DUMMY_65 = 65
    DUMMY_66 = 66
    DUMMY_67 = 67
    DUMMY_68 = 68
    DUMMY_69 = 69
    DUMMY_70 = 70
    DUMMY_71 = 71
    DUMMY_72 = 72
    DUMMY_73 = 73
    TRAPP_DOOR_74 = 74
    DOOR_75 = 75
    DUMMY_76 = 76
    SHRINE_77 = 77
    DUMMY_78 = 78
    CASKET_79 = 79
    OBELISK_80 = 80
    SHRINE_81 = 81
    DUMMY_82 = 82
    SHRINE_83 = 83
    SHRINE_84 = 84
    SHRINE_85 = 85
    DUMMY_86 = 86
    CHEST3_87 = 87
    CHEST3_88 = 88
    SARCOPHAGUS_89 = 89
    OBELISK_90 = 90
    DOOR_91 = 91
    DOOR_92 = 92
    SHRINE_93 = 93
    LARGE_URN_94 = 94
    LARGE_URN_95 = 95
    SHRINE_96 = 96
    SHRINE_97 = 97
    DOOR_98 = 98
    DOOR_99 = 99
    DURIELS_LAIR_100 = 100
    DUMMY_101 = 101
    DUMMY_102 = 102
    DUMMY_103 = 103
    ARMOR_STAND_104 = 104
    ARMOR_STAND_105 = 105
    WEAPON_RACK_106 = 106
    WEAPON_RACK_107 = 107
    MALUS_108 = 108
    SHRINE_109 = 109
    NOT_USED_110 = 110
    WELL_111 = 111
    NOT_USED_112 = 112
    WELL_113 = 113
    NOT_USED_114 = 114
    WELL_115 = 115
    SHRINE_116 = 116
    DUMMY_117 = 117
    WELL_118 = 118
    WAYPOINT_119 = 119
    DUMMY_120 = 120
    JERHYN_121 = 121
    JERHYN_122 = 122
    SHRINE_123 = 123
    SHRINE_124 = 124
    HIDDEN_STASH_125 = 125
    SKULL_PILE_126 = 126
    HIDDEN_STASH_127 = 127
    HIDDEN_STASH_128 = 128
    DOOR_129 = 129
    WELL_130 = 130
    DUMMY_131 = 131
    WELL_132 = 132
    SHRINE_133 = 133
    SHRINE_134 = 134
    SHRINE_135 = 135
    SHRINE_136 = 136
    WELL_137 = 137
    WELL_138 = 138
    CHEST_139 = 139
    CHEST_140 = 140
    CHEST_141 = 141
    JUG_142 = 142
    JUG_143 = 143
    CHEST_144 = 144
    WAYPOINT_145 = 145
    CHEST_146 = 146
    CHEST_147 = 147
    CHEST_148 = 148
    TAINTED_SUN_ALTAR_149 = 149
    SHRINE_150 = 150
    SHRINE_151 = 151
    ORIFICE_152 = 152
    DOOR_153 = 153
    CORPSE_154 = 154
    HIDDEN_STASH_155 = 155
    WAYPOINT_156 = 156
    WAYPOINT_157 = 157
    SKELETON_158 = 158
    HIDDEN_STASH_159 = 159
    FIRE_160 = 160
    FIRE_161 = 161
    FIRE_162 = 162
    HIDING_SPOT_163 = 163
    SHRINE_164 = 164
    SHRINE_165 = 165
    SHRINE_166 = 166
    SHRINE_167 = 167
    SHRINE_168 = 168
    HOLLOW_LOG_169 = 169
    SHRINE_170 = 170
    SKELETON_171 = 171
    SHRINE_172 = 172
    SHRINE_173 = 173
    LOOSE_ROCK_174 = 174
    LOOSE_BOULDER_175 = 175
    CHEST_176 = 176
    CHEST_177 = 177
    GUARD_CORPSE_178 = 178
    BOOKSHELF_179 = 179
    BOOKSHELF_180 = 180
    CHEST_181 = 181
    COFFIN_182 = 182
    CHEST_183 = 183
    SHRINE_184 = 184
    STASH_185 = 185
    STASH_186 = 186
    STASH_187 = 187
    STASH_188 = 188
    DUMMY_189 = 189
    SHRINE_190 = 190
    SHRINE_191 = 191
    TELEPORT_PAD_192 = 192
    LAM_TOME_193 = 193
    STAIR_194 = 194
    STAIR_195 = 195
    A_TRAP_196 = 196
    SHRINE_197 = 197
    CHEST_198 = 198
    SHRINE_199 = 199
    SHRINE_200 = 200
    SHRINE_201 = 201
    SHRINE_202 = 202
    STASH_203 = 203
    STASH_204 = 204
    STASH_205 = 205
    SHRINE_206 = 206
    DUMMY_207 = 207
    BASKET_208 = 208
    BASKET_209 = 209
    DUMMY_210 = 210
    DUMMY_211 = 211
    DUMMY_212 = 212
    DUMMY_213 = 213
    DUMMY_214 = 214
    DUMMY_215 = 215
    DUMMY_216 = 216
    DUMMY_217 = 217
    DUMMY_218 = 218
    DUMMY_219 = 219
    DUMMY_220 = 220
    DUMMY_221 = 221
    PILLAR_222 = 222
    COCOON_223 = 223
    COCOON_224 = 224
    SKULL_PILE_225 = 225
    SHRINE_226 = 226
    DUMMY_227 = 227
    DUMMY_228 = 228
    DOOR_229 = 229
    DOOR_230 = 230
    SHRINE_231 = 231
    SHRINE_232 = 232
    PILLAR_233 = 233
    DUMMY_234 = 234
    DUMMY_235 = 235
    SHRINE_236 = 236
    WAYPOINT_237 = 237
    WAYPOINT_238 = 238
    BODY_239 = 239
    CHEST_240 = 240
    CHEST_241 = 241
    CHEST_242 = 242
    CHEST_243 = 243
    RATNEST_244 = 244
    BODY_245 = 245
    RATNEST_246 = 246
    BED_247 = 247
    BED_248 = 248
    MANA_SHRINE_249 = 249
    A_TRAP_250 = 250
    GIDBINN_ALTAR_251 = 251
    GIDBINN_252 = 252
    DUMMY_253 = 253
    DUMMY_254 = 254
    DUMMY_255 = 255
    DUMMY_256 = 256
    DUMMY_257 = 257
    DUMMY_258 = 258
    DUMMY_259 = 259
    SHRINE_260 = 260
    A_TRAP_261 = 261
    SHRINE_262 = 262
    SHRINE_263 = 263
    SHRINE_264 = 264
    SHRINE_265 = 265
    GOO_PILE_266 = 266
    STASH = 267
    WIRTS_BODY_268 = 268
    DUMMY_269 = 269
    CORPSE_270 = 270
    CORPSE_271 = 271
    CORPSE_272 = 272
    DUMMY_273 = 273
    HIDDEN_STASH_274 = 274
    SHRINE_275 = 275
    SHRINE_276 = 276
    SHRINE_277 = 277
    SHRINE_278 = 278
    SHRINE_279 = 279
    SHRINE_280 = 280
    SHRINE_281 = 281
    SHRINE_282 = 282
    DUMMY_283 = 283
    SARCOPHAGUS_284 = 284
    DUMMY_285 = 285
    DUMMY_286 = 286
    DUMMY_287 = 287
    WAYPOINT_288 = 288
    BED_289 = 289
    DOOR_290 = 290
    DOOR_291 = 291
    DOOR_292 = 292
    DOOR_293 = 293
    DOOR_294 = 294
    DOOR_295 = 295
    DUMMY_296 = 296
    DUMMY_297 = 297
    PORTAL_298 = 298
    MAGIC_SHRINE_299 = 299
    MAGIC_SHRINE_300 = 300
    DUMMY_301 = 301
    MANA_SHRINE_302 = 302
    MAGIC_SHRINE_303 = 303
    TELEPORTATION_PAD_304 = 304
    TELEPORTATION_PAD_305 = 305
    TELEPORTATION_PAD_306 = 306
    DUMMY_307 = 307
    DUMMY_308 = 308
    DUMMY_309 = 309
    DUMMY_310 = 310
    DUMMY_311 = 311
    DUMMY_312 = 312
    DUMMY_313 = 313
    DEAD_GUARD_314 = 314
    DEAD_GUARD_315 = 315
    DEAD_GUARD_316 = 316
    DEAD_GUARD_317 = 317
    EUNUCH_318 = 318
    DUMMY_319 = 319
    MANA_SHRINE_320 = 320
    DUMMY_321 = 321
    WELL_322 = 322
    WAYPOINT_323 = 323
    WAYPOINT_324 = 324
    MAGIC_SHRINE_325 = 325
    DEAD_BODY_326 = 326
    DUMMY_327 = 327
    DUMMY_328 = 328
    CHEST_329 = 329
    CHEST_330 = 330
    CHEST_331 = 331
    CHEST_332 = 332
    CHEST_333 = 333
    CHEST_334 = 334
    CHEST_335 = 335
    CHEST_336 = 336
    STEEG_STONE_337 = 337
    GUILD_VAULT_338 = 338
    TROPHY_CASE_339 = 339
    MESSAGE_BOARD_340 = 340
    DUMMY_341 = 341
    PORTAL_342 = 342
    SHRINE_343 = 343
    SHRINE_344 = 344
    DUMMY_345 = 345
    DUMMY_346 = 346
    DUMMY_347 = 347
    DUMMY_348 = 348
    DUMMY_349 = 349
    DUMMY_350 = 350
    DUMMY_351 = 351
    DUMMY_352 = 352
    DUMMY_353 = 353
    CHEST_354 = 354
    CHEST_355 = 355
    CHEST_356 = 356
    TOME_357 = 357
    FIRE_358 = 358
    FIRE_359 = 359
    ROCK_PILE_360 = 360
    MAGIC_SHRINE_361 = 361
    BASKET_362 = 362
    HUNG_SKELETON_363 = 363
    DUMMY_364 = 364
    CASKET_365 = 365
    SEWER_STAIRS_366 = 366
    SEWER_LEVER_367 = 367
    DARK_WANDERER_368 = 368
    DUMMY_369 = 369
    DUMMY_370 = 370
    CHEST_371 = 371
    BONE_CHEST_372 = 372
    DUMMY_373 = 373
    DUMMY_374 = 374
    DUMMY_375 = 375
    HELLFORGE_376 = 376
    GUILD_PORTAL_377 = 377
    DUMMY_378 = 378
    DUMMY_379 = 379
    TRAPPED_SOUL_380 = 380
    TRAPPED_SOUL_381 = 381
    DUMMY_382 = 382
    TRAPPED_SOUL_383 = 383
    TRAPPED_SOUL_384 = 384
    DUMMY_385 = 385
    DUMMY_386 = 386
    CHEST_387 = 387
    CASKET_388 = 388
    CHEST_389 = 389
    CHEST_390 = 390
    CHEST_391 = 391
    SEAL_392 = 392
    SEAL_393 = 393
    SEAL_394 = 394
    SEAL_395 = 395
    SEAL_396 = 396
    CHEST_397 = 397
    WAYPOINT_398 = 398
    FISSURE_399 = 399
    DUMMY_400 = 400
    DUMMY_401 = 401
    WAYPOINT_402 = 402
    FIRE_403 = 403
    COMPELLING_ORB_404 = 404
    CHEST_405 = 405
    CHEST_406 = 406
    CHEST_407 = 407
    DUMMY_408 = 408
    DUMMY_409 = 409
    SIEGE_CONTROL_410 = 410
    PTOX_411 = 411
    PYOX_412 = 412
    CHEST_R_413 = 413
    SHRINE3_WILDERNESS_414 = 414
    SHRINE2_WILDERNESS_415 = 415
    HIDDEN_STASH_416 = 416
    FLAG_WILDERNESS_417 = 417
    BARREL_WILDERNESS_418 = 418
    BARREL_WILDERNESS_419 = 419
    WOOD_CHEST_L_420 = 420
    SHRINE3_WILDERNESS_421 = 421
    MANA_SHRINE_422 = 422
    HEALTH_SHRINE_423 = 423
    BURIAL_CHEST_L_424 = 424
    BURIAL_CHEST_R_425 = 425
    WELL_426 = 426
    SHRINE2_WILDERNESS_427 = 427
    SHRINE2_WILDERNESS_428 = 428
    WAYPOINT_429 = 429
    CHEST_L_430 = 430
    WOOD_CHEST_R_431 = 431
    CHEST_SL_432 = 432
    CHEST_SR_433 = 433
    ETORCH1_434 = 434
    ECFRA_435 = 435
    ETTR_436 = 436
    ETORCH2_437 = 437
    BURNING_BODIES_438 = 438
    BURNING_PIT_439 = 439
    TRIBAL_FLAG_440 = 440
    EFLG_441 = 441
    CHAN_442 = 442
    JAR1_443 = 443
    JAR2_444 = 444
    JAR3_445 = 445
    SWINGING_HEADS_446 = 446
    POLE_447 = 447
    ANIMATED_SKULL_AND_ROCKPILE_448 = 448
    GATE_449 = 449
    PILE_OF_SKULLS_AND_ROCKS_450 = 450
    HELL_GATE_451 = 451
    BANNER_1_452 = 452
    BANNER_2_453 = 453
    EXPLODING_CHEST_454 = 454
    CHEST_455 = 455
    DEATH_POLE_456 = 456
    L_DEATH_POLE_457 = 457
    ALTAR_458 = 458
    DUMMY_459 = 459
    DUMMY_460 = 460
    DUMMY_461 = 461
    DUMMY_462 = 462
    HIDDEN_STASH_463 = 463
    HEALTH_SHRINE_464 = 464
    MANA_SHRINE_465 = 465
    EVIL_URN_466 = 466
    ICE_CAVE_JAR1_467 = 467
    ICE_CAVE_JAR2_468 = 468
    ICE_CAVE_JAR3_469 = 469
    ICE_CAVE_JAR4_470 = 470
    ICE_CAVE_JAR4_471 = 471
    ICE_CAVE_SHRINE2_472 = 472
    CAGED_WUSSIE1_473 = 473
    ANCIENT_STATUE_3_474 = 474
    ANCIENT_STATUE_1_475 = 475
    ANCIENT_STATUE_2_476 = 476
    DEAD_BARBARIAN_477 = 477
    CLIENT_SMOKE_478 = 478
    ICE_CAVE_SHRINE2_479 = 479
    ICE_CAVE_TORCH1_480 = 480
    ICE_CAVE_TORCH2_481 = 481
    TTOR_482 = 482
    MANA_SHRINE_483 = 483
    HEALTH_SHRINE_484 = 484
    TOMB1_485 = 485
    TOMB2_486 = 486
    TOMB3_487 = 487
    MAGIC_SHRINE_488 = 488
    TORCH1_489 = 489
    TORCH2_490 = 490
    MANA_SHRINE_491 = 491
    HEALTH_SHRINE_492 = 492
    WELL_493 = 493
    WAYPOINT_494 = 494
    MAGIC_SHRINE_495 = 495
    WAYPOINT_496 = 496
    MAGIC_SHRINE_497 = 497
    WELL_498 = 498
    MAGIC_SHRINE2_499 = 499
    OBJECT1_500 = 500
    WOOD_CHEST_L_501 = 501
    WOOD_CHEST_R_502 = 502
    MAGIC_SHRINE_503 = 503
    WOOD_CHEST2_L_504 = 504
    WOOD_CHEST2_R_505 = 505
    SWINGING_HEADS_506 = 506
    DEBRIS_507 = 507
    PENE_508 = 508
    MAGIC_SHRINE_509 = 509
    MR_POLE_510 = 510
    WAYPOINT_511 = 511
    MAGIC_SHRINE_512 = 512
    WELL_513 = 513
    TORCH1_514 = 514
    TORCH1_515 = 515
    OBJECT1_516 = 516
    OBJECT2_517 = 517
    MR_BOX_518 = 518
    WELL_519 = 519
    MAGIC_SHRINE_520 = 520
    HEALTH_SHRINE_521 = 521
    MANA_SHRINE_522 = 522
    RED_LIGHT_523 = 523
    TOMB1_L_524 = 524
    TOMB2_L_525 = 525
    TOMB3_L_526 = 526
    UBUB_527 = 527
    SBUB_528 = 528
    TOMB1_529 = 529
    TOMB1_L_530 = 530
    TOMB2_531 = 531
    TOMB2_L_532 = 532
    TOMB3_533 = 533
    TOMB3_L_534 = 534
    MR_BOX_535 = 535
    TORCH1_536 = 536
    TORCH2_537 = 537
    CANDLES_538 = 538
    WAYPOINT_539 = 539
    DEAD_PERSON_540 = 540
    GROUND_TOMB_541 = 541
    DUMMY_542 = 542
    DUMMY_543 = 543
    GROUND_TOMB_L_544 = 544
    DEAD_PERSON2_545 = 545
    ANCIENTS_ALTAR_546 = 546
    TO_THE_WORLDSTONE_KEEP_LEVEL_1 = 547
    E_WEAPON_RACK_R_548 = 548
    E_WEAPON_RACK_L_549 = 549
    E_ARMOR_STAND_R_550 = 550
    E_ARMOR_STAND_L_551 = 551
    TORCH2_552 = 552
    FUNERAL_PYRE_553 = 553
    BURNING_LOGS_554 = 554
    STMA_555 = 555
    DEAD_PERSON2_556 = 556
    DUMMY_557 = 557
    FANA_558 = 558
    BBQB_559 = 559
    BTOR_560 = 560
    DUMMY_561 = 561
    DUMMY_562 = 562
    THE_WORLDSTONE_CHAMBER_563 = 563
    GLACIAL_CAVES_LEVEL_1_564 = 564
    STR_LAST_CINEMATIC_565 = 565
    HARROGATH_566 = 566
    ZOO_567 = 567
    KEEPER_568 = 568
    THRONE_OF_DESTRUCTION_569 = 569
    DUMMY_570 = 570
    DUMMY_571 = 571
    DUMMY_572 = 572

DeckardCains = {
    MonsterType.DECKARD_CAIN_146,
    MonsterType.DECKARD_CAIN_244,
    MonsterType.DECKARD_CAIN_245,
    MonsterType.DECKARD_CAIN_246,
    MonsterType.DECKARD_CAIN_265,
    MonsterType.DECKARD_CAIN_520,
}

TownWaypoints = {
    ObjectType.WAYPOINT_119,
    ObjectType.WAYPOINT_156,
    ObjectType.WAYPOINT_237,
    ObjectType.WAYPOINT_398,
    ObjectType.WAYPOINT_429,
}

Waypoints = {
    ObjectType.WAYPOINT_119,
    ObjectType.WAYPOINT_145,
    ObjectType.WAYPOINT_156,
    ObjectType.WAYPOINT_157,
    ObjectType.WAYPOINT_237,
    ObjectType.WAYPOINT_238,
    ObjectType.WAYPOINT_288,
    ObjectType.WAYPOINT_323,
    ObjectType.WAYPOINT_324,
    ObjectType.WAYPOINT_398,
    ObjectType.WAYPOINT_402,
    ObjectType.WAYPOINT_429,
    ObjectType.WAYPOINT_494,
    ObjectType.WAYPOINT_496,
    ObjectType.WAYPOINT_511,
    ObjectType.WAYPOINT_539,
}

class Object(Unit):
    @property
    def id(self) -> int:
        return self._internal.id

    @property
    def mode(self) -> int:
        return self._internal.dwMode

    @property
    def type(self) -> ObjectType:
        return ObjectType(self._internal.dwTxtFileNo)

    @property
    def position(self) -> Position:
        return Position(self._internal.pItemPathdwPosX, self._internal.pItemPathdwPosY)

    @property
    def act(self) -> int:
        return self._internal.dwAct

#####################################
## items                           ##
#####################################
class Quality(IntEnum):
    NONE = 0x00
    INFERIOR = 0x01
    NORMAL = 0x02
    SUPERIOR = 0x03
    MAGIC = 0x04
    SET = 0x05
    RARE = 0x06
    UNIQUE = 0x07
    CRAFT = 0x08

class Helms(StrEnum):
    # Normal Helms
    CAP = "cap"
    SKULL_CAP = "skp"
    HELM = "hlm"
    FULL_HELM = "fhl"
    GREAT_HELM = "ghm"
    CROWN = "crn"
    MASK = "msk"
    BONE_HELM = "bhm"

    # Exceptional Helms
    WAR_HAT = "xap"
    SALLET = "xkp"
    CASQUE = "xlm"
    BASINET = "xhl"
    WINGED_HELM = "xhm"
    GRAND_CROWN = "xrn"
    DEATH_MASK = "xsk"
    GRIM_HELM = "xh9"

    # Elite Helms
    SHAKO = "uap"
    HYDRASKULL = "ukp"
    ARMET = "ulm"
    GIANT_CONCH = "uhl"
    SPIRED_HELM = "uhm"
    CORONA = "urn"
    DEMONHEAD = "usk"
    BONE_VISAGE = "uh9"

class Armor(StrEnum):
    # Normal Armor
    QUILTED_ARMOR = "qui"
    LEATHER_ARMOR = "lea"
    HARD_LEATHER = "hla"
    STUDDED_LEATHER = "stu"
    RING_MAIL = "rng"
    SCALE_MAIL = "scl"
    CHAIN_MAIL = "chn"
    BREAST_PLATE = "brs"
    SPLINT_MAIL = "spl"
    PLATE_MAIL = "plt"
    FIELD_PLATE = "fld"
    GOTHIC_PLATE = "gth"
    FULL_PLATE_MAIL = "ful"
    ANCIENT_ARMOR = "aar"
    LIGHT_PLATE = "ltp"

    # Exceptional Armor
    GHOST_ARMOR = "xui"
    SERPENTSKIN_ARMOR = "xea"
    DEMONHIDE_ARMOR = "xla"
    TRELLISED_ARMOR = "xtu"
    LINKED_MAIL = "xng"
    TIGULATED_MAIL = "xcl"
    MESH_ARMOR = "xhn"
    CUIRASS = "xrs"
    RUSSET_ARMOR = "xpl"
    TEMPLAR_COAT = "xlt"
    SHARKTOOTH_ARMOR = "xld"
    EMBOSSED_PLATE = "xth"
    CHAOS_ARMOR = "xul"
    ORNATE_ARMOR = "xar"
    MAGE_PLATE = "xtp"

    # Elite Armor
    DUSK_SHROUD = "uui"
    WYRMHIDE = "uea"
    SCARAB_HUSK = "ula"
    WIRE_FLEECE = "utu"
    DIAMOND_MAIL = "ung"
    LORICATED_MAIL = "ucl"
    BONEWEAVE = "uhn"
    GREAT_HAUBERK = "urs"
    BALROG_SKIN = "upl"
    HELLFORGE_PLATE = "ult"
    KRAKEN_SHELL = "uld"
    LACQUERED_PLATE = "uth"
    SHADOW_PLATE = "uul"
    SACRED_ARMOR = "uar"
    ARCHON_PLATE = "utp"

class Shields(StrEnum):
    # Normal Shields
    BUCKLER = "buc"
    SMALL_SHIELD = "sml"
    LARGE_SHIELD = "lrg"
    KITE_SHIELD = "kit"
    TOWER_SHIELD = "tow"
    GOTHIC_SHIELD = "gts"
    BONE_SHIELD = "bsh"
    SPIKED_SHIELD = "spk"

    # Exceptional Shields
    DEFENDER = "xuc"
    ROUND_SHIELD = "xml"
    SCUTUM = "xrg"
    DRAGON_SHIELD = "xit"
    PAVISE = "xow"
    ANCIENT_SHIELD = "xts"
    GRIM_SHIELD = "xsh"
    BARBED_SHIELD = "xpk"

    # Elite Shields
    HEATER = "uuc"
    LUNA = "uml"
    HYPERION = "urg"
    MONARCH = "uit"
    AEGIS = "uow"
    WARD = "uts"
    TROLL_NEST = "ush"
    BLADE_BARRIER = "upk"

class Gloves(StrEnum):
    # Normal Gloves
    LEATHER_GLOVES = "lgl"
    HEAVY_GLOVES = "vgl"
    CHAIN_GLOVES = "mgl"
    LIGHT_GAUNTLETS = "tgl"
    GAUNTLETS = "hgl"

    # Exceptional Gloves
    DEMONHIDE_GLOVES = "xlg"
    SHARKSKIN_GLOVES = "xvg"
    HEAVY_BRACERS = "xmg"
    BATTLE_GAUNTLETS = "xtg"
    WAR_GAUNTLETS = "xhg"

    # Elite Gloves
    BRAMBLE_MITTS = "ulg"
    VAMPIREBONE_GLOVES = "uvg"
    VAMBRACES = "umg"
    CRUSADER_GAUNTLETS = "utg"
    OGRE_GAUNTLETS = "uhg"

class Boots(StrEnum):
    # Normal Boots
    BOOTS = "lbt"
    HEAVY_BOOTS = "vbt"
    CHAIN_BOOTS = "mbt"
    LIGHT_PLATE_BOOTS = "tbt"
    GREAVES = "hbt"

    # Exceptional Boots
    DEMONHIDE_BOOTS = "xlb"
    SHARKSKIN_BOOTS = "xvb"
    MESH_BOOTS = "xmb"
    BATTLE_BOOTS = "xtb"
    WAR_BOOTS = "xhb"

    # Elite Boots
    WYRMHIDE_BOOTS = "ulb"
    SCARABSHELL_BOOTS = "uvb"
    BONEWEAVE_BOOTS = "umb"
    MIRRORED_BOOTS = "utb"
    MYRMIDON_GREAVES = "uhb"

class Belts(StrEnum):
    # Normal Belts
    SASH = "lbl"
    LIGHT_BELT = "vbl"
    BELT = "mbl"
    HEAVY_BELT = "tbl"
    PLATED_BELT = "hbl"

    # Exceptional Belts
    DEMONHIDE_SASH = "zlb"
    SHARKSKIN_BELT = "zvb"
    MESH_BELT = "zmb"
    BATTLE_BELT = "ztb"
    WAR_BELT = "zhb"

    # Elite Belts
    SPIDERWEB_SASH = "ulc"
    VAMPIREFANG_BELT = "uvc"
    MITHRIL_COIL = "umc"
    TROLL_BELT = "utc"
    COLOSSUS_GIRDLE = "uhc"

class DruidPelts(StrEnum):
    # Normal Druid Pelts
    WOLF_HEAD = "dr1"
    HAWK_HELM = "dr2"
    ANTLERS = "dr3"
    FALCON_MASK = "dr4"
    SPIRIT_MASK = "dr5"

    # Exceptional Druid Pelts
    ALPHA_HELM = "dr6"
    GRIFFON_HEADRESS = "dr7"
    HUNTERS_GUISE = "dr8"
    SACRED_FEATHERS = "dr9"
    TOTEMIC_MASK = "dra"

    # Elite Druid Pelts
    BLOOD_SPIRIT = "drb"
    SUN_SPIRIT = "drc"
    EARTH_SPIRIT = "drd"
    SKY_SPIRIT = "dre"
    DREAM_SPIRIT = "drf"

class BarbarianHelms(StrEnum):
    # Normal Barbarian Helms
    JAWBONE_CAP = "ba1"
    FANGED_HELM = "ba2"
    HORNED_HELM = "ba3"
    ASSAULT_HELMET = "ba4"
    AVENGER_GUARD = "ba5"

    # Exceptional Barbarian Helms
    JAWBONE_VISOR = "ba6"
    LION_HELM = "ba7"
    RAGE_MASK = "ba8"
    SAVAGE_HELMET = "ba9"
    SLAYER_GUARD = "baa"

    # Elite Barbarian Helms
    CARNAGE_HELM = "bab"
    FURY_VISOR = "bac"
    DESTROYER_HELM = "bad"
    CONQUEROR_CROWN = "bae"
    GUARDIAN_CROWN = "baf"

class PaladinShields(StrEnum):
    # Normal Paladin Shields
    TARGE = "pa1"
    RONDACHE = "pa2"
    HERALDIC_SHIELD = "pa3"
    AERIN_SHIELD = "pa4"
    CROWN_SHIELD = "pa5"

    # Exceptional Paladin Shields
    AKARAN_TARGE = "pa6"
    AKARAN_RONDACHE = "pa7"
    PROTECTOR_SHIELD = "pa8"
    GUILDED_SHIELD = "pa9"
    ROYAL_SHIELD = "paa"

    # Elite Paladin Shields
    SACRED_TARGE = "pab"
    SACRED_RONDACHE = "pac"
    KURAST_SHIELD = "pad"
    ZAKARUM_SHIELD = "pae"
    VORTEX_SHIELD = "paf"

class NecromancerShrunkenHeads(StrEnum):
    # Normal Necromancer Shrunken Heads
    PRESERVED_HEAD = "ne1"
    ZOMBIE_HEAD = "ne2"
    UNRAVELLER_HEAD = "ne3"
    GARGOYLE_HEAD = "ne4"
    DEMON_HEAD = "ne5"

    # Exceptional Necromancer Shrunken Heads
    MUMMIFIED_TROPHY = "ne6"
    FETISH_TROPHY = "ne7"
    SEXTON_TROPHY = "ne8"
    CANTOR_TROPHY = "ne9"
    HEIROPHANT_TROPHY = "nea"

    # Elite Necromancer Shrunken Heads
    MINION_SKULL = "neb"
    HELLSPAWN_SKULL = "nec"
    OVERSEER_SKULL = "ned"
    SUCCUBAE_SKULL = "nee"
    BLOODLORD_SKULL = "nef"

class Axes(StrEnum):
    # Normal Axes
    HAND_AXE = "hax"
    AXE = "axe"
    DOUBLE_AXE = "2ax"
    MILITARY_PICK = "mpi"
    WAR_AXE = "wax"
    LARGE_AXE = "lax"
    BROAD_AXE = "bax"
    BATTLE_AXE = "btx"
    GREAT_AXE = "gax"
    GIANT_AXE = "gix"

    # Exceptional Axes
    HATCHET = "9ha"
    CLEAVER = "9ax"
    TWIN_AXE = "92a"
    CROWBILL = "9mp"
    NAGA = "9wa"
    MILITARY_AXE = "9la"
    BEARDED_AXE = "9ba"
    TABAR = "9bt"
    GOTHIC_AXE = "9ga"
    ANCIENT_AXE = "9gi"

    # Elite Axes
    TOMAHAWK = "7ha"
    SMALL_CRESCENT = "7ax"
    ETTIN_AXE = "72a"
    WAR_SPIKE = "7mp"
    BERSERKER_AXE = "7wa"
    FERAL_AXE = "7la"
    SILVER_EDGED_AXE = "7ba"
    DECAPITATOR = "7bt"
    CHAMPION_AXE = "7ga"
    GLORIOUS_AXE = "7gi"

class Maces(StrEnum):
    # Normal Maces
    CLUB = "clb"
    SPIKED_CLUB = "spc"
    MACE = "mac"
    MORNING_STAR = "mst"
    FLAIL = "fla"
    WAR_HAMMER = "whm"
    MAUL = "mau"
    GREAT_MAUL = "gma"

    # Exceptional Maces
    CUDGEL = "9cl"
    BARBED_CLUB = "9sp"
    FLANGED_MACE = "9ma"
    JAGGED_STAR = "9mt"
    KNOUT = "9fl"
    BATTLE_HAMMER = "9wh"
    WAR_CLUB = "9m9"
    MARTEL_DE_FER = "9gm"

    # Elite Maces
    TRUNCHEON = "7cl"
    TYRANT_CLUB = "7sp"
    REINFORCED_MACE = "7ma"
    DEVIL_STAR = "7mf"
    SCOURGE = "7fl"
    LEGENDARY_MAUL = "7wh"
    OGRE_MAUL = "7m7"
    THUNDER_MAUL = "7gm"

class Swords(StrEnum):
    # Normal Swords
    SHORT_SWORD = "ssd"
    SCIMITAR = "scm"
    SABER = "sbr"
    FALCHION = "flc"
    CRYSTAL_SWORD = "crs"
    BROAD_SWORD = "bsd"
    LONG_SWORD = "lsd"
    WAR_SWORD = "wsd"
    TWO_HANDED_SWORD = "2hs"
    CLAYMORE = "clm"
    GIANT_SWORD = "gis"
    BASTARD_SWORD = "bsw"
    FLAMBERGE = "flb"
    GREAT_SWORD = "gsd"

    # Exceptional Swords
    GLADIUS = "9ss"
    CUTLASS = "9sm"
    SHAMSHIR = "9sb"
    TULWAR = "9fc"
    DIMENSIONAL_BLADE = "9cr"
    BATTLE_SWORD = "9bs"
    RUNE_SWORD = "9ls"
    ANCIENT_SWORD = "9wd"
    ESPADON = "92h"
    DACIAN_FALX = "9cm"
    TUSK_SWORD = "9gs"
    GOTHIC_SWORD = "9b9"
    ZWEIHANDER = "9fb"
    EXECUTIONER_SWORD = "9gd"

    # Elite Swords
    FALCATA = "7ss"
    ATAGHAN = "7sm"
    ELEGANT_BLADE = "7sb"
    HYDRA_EDGE = "7fc"
    PHASE_BLADE = "7cr"
    CONQUEST_SWORD = "7bs"
    CRYPTIC_SWORD = "7ls"
    MYTHICAL_SWORD = "7wd"
    LEGEND_SWORD = "72h"
    HIGHLAND_BLADE = "7cm"
    BALROG_BLADE = "7gs"
    CHAMPION_SWORD = "7b7"
    COLOSSAL_SWORD = "7fb"
    COLOSSUS_BLADE = "7gd"

class Daggers(StrEnum):
    # Normal Daggers
    DAGGER = "dgr"
    DIRK = "dir"
    KRISS = "kri"
    BLADE = "bld"

    # Exceptional Daggers
    POIGNARD = "9dg"
    RONDEL = "9di"
    CINQUEDEAS = "9kr"
    STILETTO = "9bl"

    # Elite Daggers
    BONE_KNIFE = "7dg"
    MITHRAL_POINT = "7di"
    FANGED_KNIFE = "7kr"
    LEGEND_SPIKE = "7bl"

class Throwing(StrEnum):
    # Normal Throwing Weapons
    THROWING_KNIFE = "tkf"
    THROWING_AXE = "tax"
    BALANCED_KNIFE = "bkf"
    BALANCED_AXE = "bal"

    # Exceptional Throwing Weapons
    BATTLE_DART = "9tk"
    FRANCISCA = "9ta"
    WAR_DART = "9bk"
    HURLBAT = "9b8"

    # Elite Throwing Weapons
    FLYING_KNIFE = "7tk"
    FLYING_AXE = "7ta"
    WINGED_KNIFE = "7bk"
    WINGED_AXE = "7b8"

class Javelins(StrEnum):
    # Normal Javelins
    JAVELIN = "jav"
    PILUM = "pil"
    SHORT_SPEAR = "ssp"
    GLAIVE = "glv"
    THROWING_SPEAR = "tsp"

    # Exceptional Javelins
    WAR_JAVELIN = "9ja"
    GREAT_PILUM = "9pi"
    SIMBILAN = "9s9"
    SPICULUM = "9gl"
    HARPOON = "9ts"

    # Elite Javelins
    HYPERION_JAVELIN = "7ja"
    STYGIAN_PILUM = "7pi"
    BALROG_SPEAR = "7s7"
    GHOST_GLAIVE = "7gl"
    WINGED_HARPOON = "7ts"

class Spears(StrEnum):
    # Normal Spears
    SPEAR = "spr"
    TRIDENT = "tri"
    BRANDISTOCK = "brn"
    SPETUM = "spt"
    PIKE = "pik"

    # Exceptional Spears
    WAR_SPEAR = "9sr"
    FUSCINA = "9tr"
    WAR_FORK = "9br"
    YARI = "9st"
    LANCE = "9p9"

    # Elite Spears
    HYPERION_SPEAR = "7sr"
    STYGIAN_PIKE = "7tr"
    MANCATCHER = "7br"
    GHOST_SPEAR = "7st"
    WAR_PIKE = "7p7"

class Polearms(StrEnum):
    # Normal Polearms
    BARDICHE = "bar"
    VOULGE = "vou"
    SCYTHE = "scy"
    POLEAXE = "pax"
    HALBERD = "hal"
    WAR_SCYTHE = "wsc"

    # Exceptional Polearms
    LOCHABER_AXE = "9b7"
    BILL = "9vo"
    BATTLE_SCYTHE = "9s8"
    PARTIZAN = "9pa"
    BEC_DE_CORBIN = "9h9"
    GRIM_SCYTHE = "9wc"

    # Elite Polearms
    OGRE_AXE = "7o7"
    COLOSSUS_VOULGE = "7vo"
    THRESHER = "7s8"
    CRYPTIC_AXE = "7pa"
    GREAT_POLEAXE = "7h7"
    GIANT_THRESHER = "7wc"

class Bows(StrEnum):
    # Normal Bows
    SHORT_BOW = "sbw"
    HUNTERS_BOW = "hbw"
    LONG_BOW = "lbw"
    COMPOSITE_BOW = "cbw"
    SHORT_BATTLE_BOW = "sbb"
    LONG_BATTLE_BOW = "lbb"
    SHORT_WAR_BOW = "swb"
    LONG_WAR_BOW = "lwb"

    # Exceptional Bows
    EDGE_BOW = "8sb"
    RAZOR_BOW = "8hb"
    CEDAR_BOW = "8lb"
    DOUBLE_BOW = "8cb"
    SHORT_SIEGE_BOW = "8s8"
    LONG_SIEGE_BOW = "8l8"
    RUNE_BOW = "8sw"
    GOTHIC_BOW = "8lw"

    # Elite Bows
    SPIDER_BOW = "6sb"
    BLADE_BOW = "6hb"
    SHADOW_BOW = "6lb"
    GREAT_BOW = "6cb"
    DIAMOND_BOW = "6s7"
    CRUSADER_BOW = "6l7"
    WARD_BOW = "6sw"
    HYDRA_BOW = "6lw"

class Crossbows(StrEnum):
    # Normal Crossbows
    LIGHT_CROSSBOW = "lxb"
    CROSSBOW = "mxb"
    HEAVY_CROSSBOW = "hxb"
    REPEATING_CROSSBOW = "rxb"

    # Exceptional Crossbows
    ARBALEST = "8lx"
    SIEGE_CROSSBOW = "8mx"
    BALLISTA = "8hx"
    CHU_KO_NU = "8rx"

    # Elite Crossbows
    PELLET_BOW = "6lx"
    GORGON_CROSSBOW = "6mx"
    COLOSSUS_CROSSBOW = "6hx"
    DEMON_CROSSBOW = "6rx"

class Staves(StrEnum):
    # Normal Staves
    SHORT_STAFF = "sst"
    LONG_STAFF = "lst"
    GNARLED_STAFF = "gst"
    BATTLE_STAFF = "bst"
    WAR_STAFF = "wst"

    # Exceptional Staves
    JO_STAFF = "8ss"
    QUARTERSTAFF = "8ls"
    CEDAR_STAFF = "8cs"
    GOTHIC_STAFF = "8bs"
    RUNE_STAFF = "8ws"

    # Elite Staves
    WALKING_STICK = "6ss"
    STALAGMITE = "6ls"
    ELDER_STAFF = "6cs"
    SHILLELAGH = "6bs"
    ARCHON_STAFF = "6ws"

class Wands(StrEnum):
    # Normal Wands
    WAND = "wnd"
    YEW_WAND = "ywn"
    BONE_WAND = "bwn"
    GRIM_WAND = "gwn"

    # Exceptional Wands
    BURNT_WAND = "9wn"
    PETRIFIED_WAND = "9yw"
    TOMB_WAND = "9bw"
    GRAVE_WAND = "9gw"

    # Elite Wands
    POLISHED_WAND = "7wn"
    GHOST_WAND = "7yw"
    LICH_WAND = "7bw"
    UNEARTHED_WAND = "7gw"

class Scepters(StrEnum):
    # Normal Scepters
    SCEPTER = "scp"
    GRAND_SCEPTER = "gsc"
    WAR_SCEPTER = "wsp"

    # Exceptional Scepters
    RUNE_SCEPTER = "9sc"
    HOLY_WATER_SPRINKLER = "9qs"
    DIVINE_SCEPTER = "9ws"

    # Elite Scepters
    MIGHTY_SCEPTER = "7sc"
    SERAPH_ROD = "7qs"
    CADUCEUS = "7ws"

class AssassinKatars(StrEnum):
    # Normal Assassin Katars
    KATAR = "ktr"
    WRIST_BLADE = "wrb"
    HATCHET_HANDS = "axf"
    CESTUS = "ces"
    CLAWS = "clw"
    BLADE_TALONS = "btl"
    SCISSORS_KATAR = "skr"

    # Exceptional Assassin Katars
    QUHAB = "9ar"
    WRIST_SPIKE = "9wb"
    FASCIA = "9xf"
    HAND_SCYTHE = "9cs"
    GREATER_CLAWS = "9lw"
    GREATER_TALONS = "9hw"
    SCISSORS_QUHAB = "9qr"

    # Elite Assassin Katars
    SUWAYYAH = "7ar"
    WRIST_SWORD = "7wb"
    WAR_FIST = "7xf"
    BATTLE_CESTUS = "7cs"
    FERAL_CLAWS = "7lw"
    RUNIC_TALONS = "7hw"
    SCISSORS_SUWAYYAH = "7qr"

class SorceressOrbs(StrEnum):
    # Normal Sorceress Orbs
    EAGLE_ORB = "ob1"
    SACRED_GLOBE = "ob2"
    SMOKED_SPHERE = "ob3"
    CLASPED_ORB = "ob4"
    DRAGON_STONE = "ob5"

    # Exceptional Sorceress Orbs
    GLOWING_ORB = "ob6"
    CRYSTALLINE_GLOBE = "ob7"
    CLOUDY_SPHERE = "ob8"
    SPARKLING_BALL = "ob9"
    SWIRLING_CRYSTAL = "oba"

    # Elite Sorceress Orbs
    HEAVENLY_STONE = "obb"
    ELDRITCH_ORB = "obc"
    DEMON_HEART = "obd"
    VORTEX_ORB = "obe"
    DIMENSIONAL_SHARD = "obf"

class AmazonWeapons(StrEnum):
    # Normal Amazon Weapons
    STAG_BOW = "am1"
    REFLEX_BOW = "am2"
    MAIDEN_SPEAR = "am3"
    MAIDEN_PIKE = "am4"
    MAIDEN_JAVELIN = "am5"

    # Exceptional Amazon Weapons
    ASHWOOD_BOW = "am6"
    CEREMONIAL_BOW = "am7"
    CEREMONIAL_SPEAR = "am8"
    CEREMONIAL_PIKE = "am9"
    CEREMONIAL_JAVELIN = "ama"

    # Elite Amazon Weapons
    MATRIARCHAL_BOW = "amb"
    GRAND_MATRON_BOW = "amc"
    MATRIARCHAL_SPEAR = "amd"
    MATRIARCHAL_PIKE = "ame"
    MATRIARCHAL_JAVELIN = "amf"

class Circlets(StrEnum):
    CIRCLET = "ci0"
    CORONET = "ci1"
    TIARA = "ci2"
    DIADEM = "ci3"

class ThrowingPotions(StrEnum):
    RANCID_GAS_POTION = "gps"
    OIL_POTION = "ops"
    CHOKING_GAS_POTION = "gpm"
    EXPLODING_POTION = "opm"
    STRANGLING_GAS_POTION = "gpl"
    FULMINATING_POTION = "opl"

class Act1Items(StrEnum):
    WIRTS_LEG = "leg"
    HORADRIC_MALUS = "hdm"
    SCROLL_OF_INIFUSS_1 = "bks"
    SCROLL_OF_INIFUSS_2 = "bkd"

class Act2Items(StrEnum):
    BOOK_OF_SKILL = "ass"
    HORADRIC_CUBE = "box"
    HORADRIC_SCROLL = "tr1"
    STAFF_OF_KINGS = "msf"
    VIPER_AMULET = "vip"
    HORADRIC_STAFF = "hst"

class Act3Items(StrEnum):
    POTION_OF_LIFE = "xyz"
    JADE_FIGURINE = "j34"
    GOLDEN_BIRD = "g34"
    LAM_ESENS_TOME = "bbb"
    GIDBINN = "g33"
    KHALIMS_FLAIL = "qf1"
    KHALIMS_WILL = "qf2"
    KHALIMS_EYE = "qey"
    KHALIMS_HEART = "qhr"
    KHALIMS_BRAIN = "qbr"
    MEPHISTOS_SOULSTONE = "mss"

class Act4Items(StrEnum):
    HELLFORGE_HAMMER = "hfh"

class Act5Items(StrEnum):
    MALAHS_POTION = "ice"
    SCROLL_OF_RESISTANCE = "tr2"

class Gems(StrEnum):
    # Chipped Gems
    CHIPPED_AMETHYST = "gcv"
    CHIPPED_DIAMOND = "gcw"
    CHIPPED_EMERALD = "gcg"
    CHIPPED_RUBY = "gcr"
    CHIPPED_SAPPHIRE = "gcb"
    CHIPPED_SKULL = "skc"
    CHIPPED_TOPAZ = "gcy"

    # Flawed Gems
    FLAWED_AMETHYST = "gfv"
    FLAWED_DIAMOND = "gfw"
    FLAWED_EMERALD = "gfg"
    FLAWED_RUBY = "gfr"
    FLAWED_SAPPHIRE = "gfb"
    FLAWED_SKULL = "skf"
    FLAWED_TOPAZ = "gfy"

    # Normal Gems
    AMETHYST = "gsv"
    DIAMOND = "gsw"
    EMERALD = "gsg"
    RUBY = "gsr"
    SAPPHIRE = "gsb"
    SKULL = "sku"
    TOPAZ = "gsy"

    # Flawless Gems
    FLAWLESS_AMETHYST = "gzv"
    FLAWLESS_DIAMOND = "glw"
    FLAWLESS_EMERALD = "glg"
    FLAWLESS_RUBY = "glr"
    FLAWLESS_SAPPHIRE = "glb"
    FLAWLESS_SKULL = "skl"
    FLAWLESS_TOPAZ = "gly"

    # Perfect Gems
    PERFECT_AMETHYST = "gpv"
    PERFECT_DIAMOND = "gpw"
    PERFECT_EMERALD = "gpg"
    PERFECT_RUBY = "gpr"
    PERFECT_SAPPHIRE = "gpb"
    PERFECT_SKULL = "skz"
    PERFECT_TOPAZ = "gpy"

class Runes(StrEnum):
    EL = "r01"
    ELD = "r02"
    TIR = "r03"
    NEF = "r04"
    ETH = "r05"
    ITH = "r06"
    TAL = "r07"
    RAL = "r08"
    ORT = "r09"
    THUL = "r10"
    AMN = "r11"
    SOL = "r12"
    SHAEL = "r13"
    DOL = "r14"
    HEL = "r15"
    IO = "r16"
    LUM = "r17"
    KO = "r18"
    FAL = "r19"
    LEM = "r20"
    PUL = "r21"
    UM = "r22"
    MAL = "r23"
    IST = "r24"
    GUL = "r25"
    VEX = "r26"
    OHM = "r27"
    LO = "r28"
    SUR = "r29"
    BER = "r30"
    JAH = "r31"
    CHAM = "r32"
    ZOD = "r33"

class Potions(StrEnum):
    ANTIDOTE_POTION = "yps"
    STAMINA_POTION = "vps"
    THAWING_POTION = "wms"
    MINOR_HEALING_POTION = "hp1"
    MINOR_MANA_POTION = "mp1"
    LIGHT_HEALING_POTION = "hp2"
    LIGHT_MANA_POTION = "mp2"
    HEALING_POTION = "hp3"
    MANA_POTION = "mp3"
    GREATER_HEALING_POTION = "hp4"
    GREATER_MANA_POTION = "mp4"
    SUPER_HEALING_POTION = "hp5"
    SUPER_MANA_POTION = "mp5"
    REJUV_POTION = "rvs"
    FULL_REJUV_POTION = "rvl"

class Charms(StrEnum):
    SMALL_CHARM = "cm1"
    LARGE_CHARM = "cm2"
    GRAND_CHARM = "cm3"

class Scrolls(StrEnum):
    IDENTIFY_SCROLL = "isc"
    TOWN_PORTAL_SCROLL = "tsc"

class Tomes(StrEnum):
    TOME_OF_TOWN_PORTAL = "tbk"
    TOME_OF_IDENTIFY = "ibk"

class Miscellaneous(StrEnum):
    ARROWS = "aqv"
    BOLTS = "cqv"
    JEWEL = "jew"
    SKELETON_KEY = "key"
    AMULET = "amu"
    GOLD = "gld"
    RING = "rin"
    EAR = "ear"

class UnusedItems(StrEnum):
    TORCH = "tch"
    HEART = "hrt"
    BRAIN = "brz"
    JAWBONE = "jaw"
    EYE = "eyz"
    HORN = "hrn"
    HERB = "hrb"
    TAIL = "tal"
    FLAG = "flg"
    FANG = "fng"
    QUILL = "qll"
    SOUL = "sol"
    SCALP = "scz"
    SPLEEN = "spe"
    BLACK_TOWER_KEY = "luv"
    ELIXIR = "elx"
    SCROLL_OF_KNOWLEDGE = "0sc"

class ItemType(StrEnum):
    UNKNOWN = 'unk'


#####################################
## stats                           ##
#####################################
class StatType(IntEnum):
    STRENGTH = 0
    ENERGY = 1
    DEXTERITY = 2
    VITALITY = 3
    STAT_POINTS_LEFT = 4
    NEW_SKILLS = 5
    HP = 6
    MAX_HP = 7
    MANA = 8
    MAX_MANA = 9
    STAMINA = 10
    MAX_STAMINA = 11
    LEVEL = 12
    EXP = 13
    GOLD = 14
    GOLD_BANK = 15
    ENHANCED_DEFENSE = 16
    ENHANCED_MAXIMUM_DAMAGE = 17
    ENHANCED_MINIMUM_DAMAGE = 18
    ATTACK_RATING = 19
    TO_BLOCK = 20
    MINIMUM_DAMAGE = 21
    MAXIMUM_DAMAGE = 22
    SECONDARY_MINIMUM_DAMAGE = 23
    SECONDARY_MAXIMUM_DAMAGE = 24
    ENHANCED_DAMAGE = 25
    MANA_RECOVERY = 26
    MANA_RECOVERY_BONUS = 27
    STAMINA_RECOVERY_BONUS = 28
    LAST_EXPERIENCE = 29
    NEXT_EXPERIENCE = 30
    DEFENSE = 31
    DEFENSE_VS_MISSILES = 32
    DEFENSE_VS_MELEE = 33
    DMG_REDUCTION = 34
    MAGIC_DMG_REDUCTION = 35
    DMG_REDUCTION_PCT = 36
    MAGIC_DMG_REDUCTION_PCT = 37
    MAX_MAGIC_DMG_REDUCT_PCT = 38
    FIRE_RESIST = 39
    MAX_FIRE_RESIST = 40
    LIGHTNING_RESIST = 41
    MAX_LIGHTNING_RESIST = 42
    COLD_RESIST = 43
    MAX_COLD_RESIST = 44
    POISON_RESIST = 45
    MAX_POISON_RESIST = 46
    DAMAGE_AURA = 47
    MINIMUM_FIRE_DAMAGE = 48
    MAXIMUM_FIRE_DAMAGE = 49
    MINIMUM_LIGHTNING_DAMAGE = 50
    MAXIMUM_LIGHTNING_DAMAGE = 51
    MINIMUM_MAGICAL_DAMAGE = 52
    MAXIMUM_MAGICAL_DAMAGE = 53
    MINIMUM_COLD_DAMAGE = 54
    MAXIMUM_COLD_DAMAGE = 55
    COLD_DAMAGE_LENGTH = 56
    MINIMUM_POISON_DAMAGE = 57
    MAXIMUM_POISON_DAMAGE = 58
    POISON_DAMAGE_LENGTH = 59
    LIFE_LEECH = 60
    MAX_LIFE_STOLEN_PER_HIT = 61
    MANA_LEECH = 62
    MAX_MANA_STOLEN_PER_HIT = 63
    MINIMUM_STAMINA_DRAIN = 64
    MAXIMUM_STAMINA_DRAIN = 65
    STUN_LENGTH = 66
    VELOCITY_PERCENT = 67
    ATTACK_RATE = 68
    OTHER_ANIMATION_RATE = 69
    AMMO_QUANTITY = 70
    VALUE = 71
    DURABILITY = 72
    MAX_DURABILITY = 73
    REPLENISH_LIFE = 74
    ENHANCED_MAX_DURABILITY = 75
    ENHANCED_LIFE = 76
    ENHANCED_MANA = 77
    ATTACKER_TAKES_DAMAGE = 78
    GOLD_FIND = 79
    MAGIC_FIND = 80
    KNOCKBACK = 81
    TIME_DURATION = 82
    CLASS_SKILLS = 83
    UNSENT_PARAMETER = 84
    ADD_EXPERIENCE = 85
    LIFE_AFTER_EACH_KILL = 86
    REDUCE_VENDOR_PRICES = 87
    DOUBLE_HERB_DURATION = 88
    LIGHT_RADIUS = 89
    LIGHT_COLOUR = 90
    REDUCED_REQUIREMENTS = 91
    REDUCED_LEVEL_REQ = 92
    INCREASED_ATTACK_SPEED = 93
    REDUCED_LEVEL_REQ_PCT = 94
    LAST_BLOCK_FRAME = 95
    FASTER_RUN_WALK = 96
    NON_CLASS_SKILL = 97
    STATE = 98
    FASTER_HIT_RECOVERY = 99
    MONSTER_PLAYER_COUNT = 100
    SKILL_POISON_OVERRIDE_LEN = 101
    FASTER_BLOCK = 102
    SKILL_BYPASS_UNDEAD = 103
    SKILL_BYPASS_DEMONS = 104
    FASTER_CAST = 105
    SKILL_BYPASS_BEASTS = 106
    SINGLE_SKILL = 107
    SLAIN_MONSTERS_RIP = 108
    CURSE_RESISTANCE = 109
    POISON_LENGTH_REDUCTION = 110
    ADDS_DAMAGE = 111
    HIT_CAUSES_MONSTER_TO_FLEE = 112
    HIT_BLINDS_TARGET = 113
    DAMAGE_TO_MANA = 114
    IGNORE_TARGETS_DEFENSE = 115
    REDUCE_TARGETS_DEFENSE = 116
    PREVENT_MONSTER_HEAL = 117
    HALF_FREEZE_DURATION = 118
    TO_HIT_PERCENT = 119
    MONSTER_DEF_DUCT_PER_HIT = 120
    DAMAGE_TO_DEMONS = 121
    DAMAGE_TO_UNDEAD = 122
    ATTACK_RATING_VS_DEMONS = 123
    ATTACK_RATING_VS_UNDEAD = 124
    THROWABLE = 125
    ELEMENTAL_SKILLS = 126
    ALL_SKILLS = 127
    ATTACKER_TAKES_LTNG_DMG = 128
    IRON_MAIDEN_LEVEL = 129
    LIFE_TAP_LEVEL = 130
    THORNS_PERCENT = 131
    BONE_ARMOR = 132
    MAXIMUM_BONE_ARMOR = 133
    FREEZE_TARGET = 134
    OPEN_WOUNDS = 135
    CRUSHING_BLOW = 136
    KICK_DAMAGE = 137
    MANA_AFTER_EACH_KILL = 138
    LIFE_AFTER_EACH_DEMON_KILL = 139
    EXTRA_BLOOD = 140
    DEADLY_STRIKE = 141
    FIRE_ABSORB_PERCENT = 142
    FIRE_ABSORB = 143
    LIGHTNING_ABSORB_PERCENT = 144
    LIGHTNING_ABSORB = 145
    MAGIC_ABSORB_PERCENT = 146
    MAGIC_ABSORB = 147
    COLD_ABSORB_PERCENT = 148
    COLD_ABSORB = 149
    SLOW = 150
    AURA = 151
    INDESTRUCTIBLE = 152
    CANNOT_BE_FROZEN = 153
    STAMINA_DRAIN_PERCENT = 154
    REANIMATE = 155
    PIERCING_ATTACK = 156
    FIRES_MAGIC_ARROWS = 157
    FIRE_EXPLOSIVE_ARROWS = 158
    MINIMUM_THROWING_DAMAGE = 159
    MAXIMUM_THROWING_DAMAGE = 160
    SKILL_HAND_OF_ATHENA = 161
    SKILL_STAMINA_PERCENT = 162
    SKILL_PASSIVE_STAMINA_PCT = 163
    CONCENTRATION = 164
    ENCHANT = 165
    PIERCE = 166
    CONVICTION = 167
    CHILLING_ARMOR = 168
    FRENZY = 169
    DECREPIFY = 170
    SKILL_ARMOR_PERCENT = 171
    ALIGNMENT = 172
    TARGET_0 = 173
    TARGET_1 = 174
    GOLD_LOST = 175
    CONVERSION_LEVEL = 176
    CONVERSION_MAXIMUM_LIFE = 177
    UNIT_DO_OVERLAY = 178
    ATTACK_RATING_VS_MONSTER_TYPE = 179
    DAMAGE_TO_MONSTER_TYPE = 180
    FADE = 181
    ARMOR_OVERRIDE_PERCENT = 182
    UNUSED_183 = 183
    UNUSED_184 = 184
    UNUSED_185 = 185
    UNUSED_186 = 186
    UNUSED_187 = 187
    SKILL_TAB = 188
    UNUSED_189 = 189
    UNUSED_190 = 190
    UNUSED_191 = 191
    UNUSED_192 = 192
    UNUSED_193 = 193
    SOCKETS = 194
    SKILL_ON_STRIKING = 195
    SKILL_ON_KILL = 196
    SKILL_ON_DEATH = 197
    SKILL_ON_HIT = 198
    SKILL_ON_LEVEL_UP = 199
    UNUSED_200 = 200
    SKILL_WHEN_STRUCK = 201
    UNUSED_202 = 202
    UNUSED_203 = 203
    CHARGED = 204
    UNUSED_205 = 205
    UNUSED_206 = 206
    UNUSED_207 = 207
    UNUSED_208 = 208
    UNUSED_209 = 209
    UNUSED_210 = 210
    UNUSED_211 = 211
    UNUSED_212 = 212
    DEFENSE_PER_LEVEL = 213
    ENHANCED_DEFENSE_PER_LEVEL = 214
    LIFE_PER_LEVEL = 215
    MANA_PER_LEVEL = 216
    MAX_DAMAGE_PER_LEVEL = 217
    MAX_ENHANCED_DMG_PER_LEVEL = 218
    STRENGTH_PER_LEVEL = 219
    DEXTERITY_PER_LEVEL = 220
    ENERGY_PER_LEVEL = 221
    VITALITY_PER_LEVEL = 222
    ATTACK_RATING_PER_LEVEL = 223
    BONUS_ATTACK_RATING_PER_LEVEL = 224
    MAX_COLD_DAMAGE_PER_LEVEL = 225
    MAX_FIRE_DAMAGE_PER_LEVEL = 226
    MAX_LIGHTNING_DAMAGE_PER_LEVEL = 227
    MAX_POISON_DAMAGE_PER_LEVEL = 228
    COLD_RES_PER_LEVEL = 229
    FIRE_RES_PER_LEVEL = 230
    LIGHTNING_RES_PER_LEVEL = 231
    POISON_RES_PER_LEVEL = 232
    COLD_ABSORB_PER_LEVEL = 233
    FIRE_ABSORB_PER_LEVEL = 234
    LIGHTNING_ABSORB_PER_LEVEL = 235
    POISON_ABSORB_PER_LEVEL = 236
    THORNS_PER_LEVEL = 237
    EXTRA_GOLD_PER_LEVEL = 238
    MAGIC_FIND_PER_LEVEL = 239
    STAMINA_REGEN_PER_LEVEL = 240
    STAMINA_PER_LEVEL = 241
    DAMAGE_TO_DEMONS_PER_LEVEL = 242
    DAMAGE_TO_UNDEAD_PER_LEVEL = 243
    ATTACK_RATING_VS_DEMONS_PER_LEVEL = 244
    ATTACK_RATING_VS_UNDEAD_PER_LEVEL = 245
    CRUSHING_BLOW_PER_LEVEL = 246
    OPEN_WOUNDS_PER_LEVEL = 247
    KICK_DAMAGE_PER_LEVEL = 248
    DEADLY_STRIKE_PER_LEVEL = 249
    FIND_GEMS_PER_LEVEL = 250
    REPAIRS_DURABILITY = 251
    REPLENISHES_QUANTITY = 252
    INCREASED_STACK_SIZE = 253
    FIND_ITEM = 254
    SLASH_DAMAGE = 255
    SLASH_DAMAGE_PERCENT = 256
    CRUSH_DAMAGE = 257
    CRUSH_DAMAGE_PERCENT = 258
    THRUST_DAMAGE = 259
    THRUST_DAMAGE_PERCENT = 260
    SLASH_DAMAGE_ABSORPTION = 261
    CRUSH_DAMAGE_ABSORPTION = 262
    THRUST_DAMAGE_ABSORPTION = 263
    SLASH_DAMAGE_ABSORB_PCT = 264
    CRUSH_DAMAGE_ABSORB_PCT = 265
    THRUST_DAMAGE_ABSORB_PCT = 266
    DEFENSE_PER_TIME = 267
    ENHANCED_DEFENSE_PER_TIME = 268
    LIFE_PER_TIME = 269
    MANA_PER_TIME = 270
    MAX_DAMAGE_PER_TIME = 271
    MAX_ENHANCED_DMG_PER_TIME = 272
    STRENGTH_PER_TIME = 273
    DEXTERITY_PER_TIME = 274
    ENERGY_PER_TIME = 275
    VITALITY_PER_TIME = 276
    ATTACK_RATING_PER_TIME = 277
    CHANCE_TO_HIT_PER_TIME = 278
    MAX_COLD_DAMAGE_PER_TIME = 279
    MAX_FIRE_DAMAGE_PER_TIME = 280
    MAX_LIGHTNING_DAMAGE_PER_TIME = 281
    MAX_DAMAGE_PER_POISON = 282
    COLD_RES_PER_TIME = 283
    FIRE_RES_PER_TIME = 284
    LIGHTNING_RES_PER_TIME = 285
    POISON_RES_PER_TIME = 286
    COLD_ABSORPTION_PER_TIME = 287
    FIRE_ABSORPTION_PER_TIME = 288
    LIGHTNING_ABSORB_PER_TIME = 289
    POISON_ABSORB_PER_TIME = 290
    EXTRA_GOLD_PER_TIME = 291
    MAGIC_FIND_PER_TIME = 292
    REGEN_STAMINA_PER_TIME = 293
    STAMINA_PER_TIME = 294
    DAMAGE_TO_DEMONS_PER_TIME = 295
    DAMAGE_TO_UNDEAD_PER_TIME = 296
    ATTACK_RATING_VS_DEMONS_PER_TIME = 297
    ATTACK_RATING_VS_UNDEAD_PER_TIME = 298
    CRUSHING_BLOW_PER_TIME = 299
    OPEN_WOUNDS_PER_TIME = 300
    KICK_DAMAGE_PER_TIME = 301
    DEADLY_STRIKE_PER_TIME = 302
    FIND_GEMS_PER_TIME = 303
    ENEMY_COLD_RES_REDUCTION = 304
    ENEMY_FIRE_RES_REDUCTION = 305
    ENEMY_LIGHT_RES_REDUCTION = 306
    ENEMY_POISON_RES_REDUCTION = 307
    DAMAGE_VS_MONSTERS = 308
    ENHANCED_DMG_VS_MONSTERS = 309
    ATTACK_RATING_VS_MONSTERS = 310
    BONUS_ATTACK_RATING_VS_MONSTERS = 311
    DEFENSE_VS_MONSTERS = 312
    ENHANCED_DEF_VS_MONSTERS = 313
    FIRE_DAMAGE_LENGTH = 314
    MIN_FIRE_DAMAGE_LENGTH = 315
    MAX_FIRE_DAMAGE_LENGTH = 316
    PROGRESSIVE_DAMAGE = 317
    PROGRESSIVE_STEAL = 318
    PROGRESSIVE_OTHER = 319
    PROGRESSIVE_FIRE = 320
    PROGRESSIVE_COLD = 321
    PROGRESSIVE_LIGHTNING = 322
    EXTRA_CHARGES = 323
    PROGRESSIVE_ATTACK_RATING = 324
    POISON_COUNT = 325
    DAMAGE_FRAME_RATE = 326
    PIERCE_IDX = 327
    FIRE_MASTERY = 328
    LIGHTNING_MASTERY = 329
    COLD_MASTERY = 330
    POISON_MASTERY = 331
    PASSIVE_ENEMY_FIRE_RES_REDUC = 332
    PASSIVE_ENEMY_LIGHTNING_RES_REDUC = 333
    PASSIVE_ENEMY_COLD_RES_REDUC = 334
    PASSIVE_ENEMY_POISON_RES_REDUC = 335
    CRITICAL_STRIKE = 336
    DODGE = 337
    AVOID = 338
    EVADE = 339
    WARMTH = 340
    MELEE_ARM_MASTERY = 341
    MELEE_DAMAGE_MASTERY = 342
    MELEE_CRIT_HIT_MASTERY = 343
    THROWN_WEAPON_ARM_MASTERY = 344
    THROWN_WEAPON_DMG_MASTERY = 345
    THROWN_CRIT_HIT_MASTERY = 346
    WEAPON_BLOCK = 347
    SUMMON_RESIST = 348
    MODIFIER_LIST_SKILL = 349
    MODIFIER_LIST_LEVEL = 350
    LAST_SENT_LIFE_PERCENT = 351
    SOURCE_UNIT_TYPE = 352
    SOURCE_UNIT_ID = 353
    SHORT_PARAMETER_1 = 354
    QUEST_ITEM_DIFFICULTY = 355
    PASSIVE_MAGIC_DMG_MASTERY = 356
    PASSIVE_MAGIC_RES_REDUC = 357

@dataclass
class Stat:
    def __init__(self, type: StatType, value: int):
        self.type = type
        self.value = value

ItemTypeDict = {item.name: item.value for category in [
    Helms, Armor, Shields, Gloves, Boots, Belts, DruidPelts, BarbarianHelms,
    PaladinShields, NecromancerShrunkenHeads, Axes, Maces, Swords, Daggers,
    Throwing, Javelins, Spears, Polearms, Bows, Crossbows, Staves, Wands,
    Scepters, AssassinKatars, SorceressOrbs, AmazonWeapons, Circlets,
    ThrowingPotions, Act1Items, Act2Items, Act3Items, Act4Items, Act5Items,
    Gems, Runes, Potions, Charms, Scrolls, Tomes, Miscellaneous, UnusedItems
] for item in category}

ItemType = StrEnum('ItemType', {**ItemType.__members__, **ItemTypeDict})

@dataclass
class ItemFlags:
    identified: bool
    switched_in: bool
    switched_out: bool
    broken: bool
    has_sockets: bool
    in_store: bool
    is_ear: bool
    start_item: bool
    compact_save: bool
    ethereal: bool
    personalized: bool
    runeword: bool

class ItemLocation(IntEnum):
    INVENTORY = 0x00
    EQUIPPED = 0x01
    BELT = 0x02
    CUBE = 0x03
    STASH = 0x04
    NULL = 0xFF

class Item(Unit):
    @property
    def owner(self) -> Optional[Character]:
        addr = self._internal.pItemDatadpOwner
        if not addr:
            return None
        return Character(game.build_player_unit_from_ptr(addr))

    @property
    def type(self) -> ItemType:
        try:
            return ItemType(game.get_item_code(self._internal.dwTxtFileNo))
        except:
            return ItemType.UNKNOWN

    @property
    def level(self) -> int:
        return self._internal.pItemDatadwItemLevel

    @property
    def flags(self) -> ItemFlags:
        value: int = self._internal.pItemDatadwFlags
        def check(flag: int) -> bool:
            return (value & flag) == flag
        return ItemFlags(
            check(0x00000010),
            check(0x00000040),
            check(0x00000080),
            check(0x00000100),
            check(0x00000800),
            check(0x00002000),
            check(0x00010000),
            check(0x00020000),
            check(0x00200000),
            check(0x00400000),
            check(0x01000000),
            check(0x04000000),
        )

    @property
    def quality(self) -> Quality:
        return Quality(self._internal.pItemDatadwQuality)

    @property
    def position(self) -> Position:
        return Position(
            self._internal.pItemPathdwPosX,
            self._internal.pItemPathdwPosY
        )

    @property
    def stats(self) -> list[Stat]:
        raw_stats = game.get_item_stats(self._internal)
        if raw_stats is None:
            return []

        return [Stat(StatType(stat_index), value) for stat_index, _, value in raw_stats]

#####################################
## drawing                         ##
#####################################
class TextColor(IntEnum):
    Disabled = -1
    White = 0
    Red = 1
    Green = 2
    Blue = 3
    Gold = 4
    Gray = 5
    Black = 6
    Tan = 7
    Orange = 8
    Yellow = 9
    DarkGreen = 10
    Purple = 11
    Silver = 15

PaletteColor: TypeAlias = int  # 1 byte (0-255)

@dataclass
class Element:
    def _to_dict(self) -> dict[str, any]:
        return {
            "text": "",
            "color": 0,
            "x1": 0,
            "y1": 0,
            "x2": 0,
            "y2": 0,
        }

@dataclass
class TextElement(Element):
    text: str
    color: TextColor
    position: Position

    def _to_dict(self) -> dict[str, any]:
        return {
            "text": self.text,
            "color": self.color.value,
            "x1": self.position.x,
            "y1": self.position.y,
            "x2": 0,
            "y2": 0,
        }

@dataclass
class LineElement(Element):
    begin: Position
    end: Position
    color: PaletteColor

    def _to_dict(self) -> dict[str, any]:
        return {
            "text": "",
            "color": self.color,
            "x1": self.begin.x,
            "y1": self.begin.y,
            "x2": self.end.x,
            "y2": self.end.y,
        }

@dataclass
class CrossElement(Element):
    color: PaletteColor
    position: Position

    def _to_dict(self) -> dict[str, any]:
        return {
            "text": "",
            "color": self.color,
            "x1": self.position.x,
            "y1": self.position.y,
            "x2": 0,
            "y2": 0,
        }

#####################################
## world                           ##
#####################################
class WorldMeta:
    @property
    def closest_waypoint(self) -> Optional[Object]:
        for unit in get_nearby_units():
            if isinstance(unit, Object):
                if unit.type in Waypoints:
                    return unit
        return None


World = WorldMeta()

#####################################
## functions                       ##
#####################################
def get_game() -> Optional[Game]:
    internal = game.get_game_info()
    return Game(internal) if internal else None

def get_player() -> Optional[Character]:
    internal = game.get_player_unit()
    return Character(internal) if internal else None

def get_all_controls() -> list[Control]:
    results: list[Control] = []
    for control in game.get_all_controls():
        results.append(Control(control))
    return results

def get_all_items() -> list[Item]:
    return [u for u in get_nearby_units() if isinstance(u, Item)]

def get_all_monsters() -> list[Monster]:
    return [u for u in get_nearby_units() if isinstance(u, Monster)]

def get_nearby_units() -> list[Unit]:
    results = []
    for unit in game.get_nearby_units():
        t = unit.type
        if t == UnitType.OBJECT:
            results.append(Object(unit))
        elif t == UnitType.MONSTER:
            results.append(Monster(unit))
        elif t == UnitType.PLAYER:
            results.append(Character(unit))
        else:
            results.append(unit)
    return results

def reveal_automap() -> None:
    game.reveal_automap()

def pick_up(item: Item) -> None:
    game.pick_up(item.id, 4)

#####################################
## helpers                         ##
#####################################
def info(message: str):
    write_log("INF", message)

def warn(message: str):
    write_log("WRN", message)

def error(message: str):
    write_log("ERR", message)

def debug(message: str):
    write_log("DBG", message)

def print_game(color: TextColor, message: str):
    game.print_game_string(message, color)

def write_log(level: str, message: str):
    game.write_log(level, message)

def distance(begin: Position, end: Position):
    return math.sqrt((begin.x - end.x) ** 2 + (begin.y - end.y) ** 2)

class LoopType(StrEnum):
    FLEX = "FLEX"
    DRAW_AUTOMAP = "DRAW_AUTOMAP"
    CLIENT_STATE = "CLIENT_STATE"

_pending_tasks = {}
_client_state_handlers: dict[ClientState, list[Callable[[], None]]] = defaultdict(list)
def loop(loop_type: LoopType, state: ClientState = None):
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        async def runner():
            try:
                if is_async:
                    await func()
                else:
                    func()
            except Exception:
                error(traceback.format_exc())

        def wrapped():
            global _asyncio_loop
            if func in _pending_tasks and not _pending_tasks[func].done():
                return

            _pending_tasks[func] = asyncio.run_coroutine_threadsafe(runner(), _asyncio_loop)

        match loop_type:
            case LoopType.FLEX:
                game.register_flex_loop(wrapped)
            case LoopType.DRAW_AUTOMAP:
                game.register_draw_automap_loop(func)
            case LoopType.CLIENT_STATE:
                if not state:
                    warn(f"Missing client state for {func.__name__}")
                else:
                    _client_state_handlers[state].append(wrapped)
            case _:
                warn(f"Unknown loop type {loop_type} on {func.__name__}")

        return wrapped

    return decorator

_last_client_state = None
@loop(LoopType.FLEX)
def _client_state_loop():
    global _last_client_state
    state = get_client_state()
    for func in _client_state_handlers.get(state, []):
        func()

async def pause(milliseconds: int):
    await asyncio.sleep(milliseconds / 1000)
