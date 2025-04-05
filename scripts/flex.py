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

import game
import math
from typing import Optional, TypeAlias, Callable, Awaitable
from dataclasses import dataclass
from enum import IntEnum, StrEnum, Enum, auto
from game import wstring_at
import asyncio
import inspect
import threading

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
## structures                      ##
#####################################
@dataclass
class Position:
    x: int
    y: int

@dataclass
class Dimensions:
    width: int
    height: int

class Unit:
    def __init__(self, unit: game.Unit):
        self._internal_unit = unit

    @property
    def id(self) -> int:
        return self._internal_unit.id

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
            self._internal_unit.pPathxPos,
            self._internal_unit.pPathyPos
        )

    @property
    def act(self) -> Act:
        return Act(self._internal_unit.dwAct)

@dataclass
class MonsterTier:
    normal: bool
    minion: bool
    champion: bool
    boss: bool

class Monster(Unit):
    @property
    def name(self) -> str:
        addr = self._internal_unit.pMonsterDatawName
        if not addr:
            return ""
        return wstring_at(addr)

    @property
    def type(self) -> int:
        return self._internal_unit.dwTxtFileNo

    @property
    def mode(self) -> int:
        return self._internal_unit.dwMode

    @property
    def position(self) -> Position:
        return Position(
            self._internal_unit.pPathxPos,
            self._internal_unit.pPathyPos
        )

    @property
    def tier(self) -> MonsterTier:
        return MonsterTier(
            normal = self._internal_unit.pMonsterDatafNormal,
            minion = self._internal_unit.pMonsterDatafMinion,
            champion = self._internal_unit.pMonsterDatafChamp,
            boss =  self._internal_unit.pMonsterDatafBoss
        )

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
        addr = self._internal_unit.pItemDatadpOwner
        if not addr:
            return None
        return Character(game.build_player_unit_from_ptr(addr))

    @property
    def type(self) -> ItemType:
        try:
            return ItemType(game.get_item_code(self._internal_unit.dwTxtFileNo))
        except:
            return ItemType.UNKNOWN

    @property
    def level(self) -> int:
        return self._internal_unit.pItemDatadwItemLevel

    @property
    def flags(self) -> ItemFlags:
        value: int = self._internal_unit.pItemDatadwFlags
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
        return Quality(self._internal_unit.pItemDatadwQuality)

    @property
    def position(self) -> Position:
        return Position(
            self._internal_unit.pItemPathdwPosX,
            self._internal_unit.pItemPathdwPosY
        )

    @property
    def stats(self) -> list[Stat]:
        raw_stats = game.get_item_stats(self._internal_unit)
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
    results: list[Item] = []
    for unit in game.get_item_table():
        if not unit or unit.id == 0:
            continue
        results.append(Item(unit))
    return results

def get_all_monsters() -> list[Monster]:
    results: list[Monster] = []
    for unit in game.get_monster_table():
        if not unit or unit.id == 0:
            continue
        results.append(Monster(unit))
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
                game.register_draw_automap_loop(wrapped)
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
