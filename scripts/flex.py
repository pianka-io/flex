import math
import game
from dataclasses import dataclass
from enum import IntEnum, StrEnum


#####################################
## structures                      ##
#####################################
@dataclass
class Position:
    x: int
    y: int


class Unit:
    def __init__(self, unit: game.Unit):
        self.internal_unit = unit

    @property
    def id(self) -> int:
        return self.internal_unit.id


#####################################
## characters                      ##
#####################################
class Character(Unit):
    @property
    def position(self) -> Position:
        return Position(
            self.internal_unit.pPathxPos,
            self.internal_unit.pPathyPos
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
    STATPOINTSLEFT = 4
    NEWSKILLS = 5
    HP = 6
    MAXHP = 7
    MANA = 8
    MAXMANA = 9
    STAMINA = 10
    MAXSTAMINA = 11
    LEVEL = 12
    EXP = 13
    GOLD = 14
    GOLDBANK = 15
    ENHANCEDDEFENSE = 16
    ENHANCEDMAXIMUMDAMAGE = 17
    ENHANCEDMINIMUMDAMAGE = 18
    ATTACKRATING = 19
    TOBLOCK = 20
    MINIMUMDAMAGE = 21
    MAXIMUMDAMAGE = 22
    SECONDARYMINIMUMDAMAGE = 23
    SECONDARYMAXIMUMDAMAGE = 24
    ENHANCEDDAMAGE = 25
    MANARECOVERY = 26
    MANARECOVERYBONUS = 27
    STAMINARECOVERYBONUS = 28
    LASTEXPERIENCE = 29
    NEXTEXPERIENCE = 30
    DEFENSE = 31
    DEFENSEVSMISSILES = 32
    DEFENSEVSMELEE = 33
    DMGREDUCTION = 34
    MAGICDMGREDUCTION = 35
    DMGREDUCTIONPCT = 36
    MAGICDMGREDUCTIONPCT = 37
    MAXMAGICDMGREDUCTPCT = 38
    FIRERESIST = 39
    MAXFIRERESIST = 40
    LIGHTNINGRESIST = 41
    MAXLIGHTNINGRESIST = 42
    COLDRESIST = 43
    MAXCOLDRESIST = 44
    POISONRESIST = 45
    MAXPOISONRESIST = 46
    DAMAGEAURA = 47
    MINIMUMFIREDAMAGE = 48
    MAXIMUMFIREDAMAGE = 49
    MINIMUMLIGHTNINGDAMAGE = 50
    MAXIMUMLIGHTNINGDAMAGE = 51
    MINIMUMMAGICALDAMAGE = 52
    MAXIMUMMAGICALDAMAGE = 53
    MINIMUMCOLDDAMAGE = 54
    MAXIMUMCOLDDAMAGE = 55
    COLDDAMAGELENGTH = 56
    MINIMUMPOISONDAMAGE = 57
    MAXIMUMPOISONDAMAGE = 58
    POISONDAMAGELENGTH = 59
    LIFELEECH = 60
    MAXLIFESTOLENPERHIT = 61
    MANALEECH = 62
    MAXMANASTOLENPERHIT = 63
    MINIMUMSTAMINADRAIN = 64
    MAXIMUMSTAMINADRAIN = 65
    STUNLENGTH = 66
    VELOCITYPERCENT = 67
    ATTACKRATE = 68
    OTHERANIMATIONRATE = 69
    AMMOQUANTITY = 70
    VALUE = 71
    DURABILITY = 72
    MAXDURABILITY = 73
    REPLENISHLIFE = 74
    ENHANCEDMAXDURABILITY = 75
    ENHANCEDLIFE = 76
    ENHANCEDMANA = 77
    ATTACKERTAKESDAMAGE = 78
    GOLDFIND = 79
    MAGICFIND = 80
    KNOCKBACK = 81
    TIMEDURATION = 82
    CLASSSKILLS = 83
    UNSENTPARAMETER = 84
    ADDEXPERIENCE = 85
    LIFEAFTEREACHKILL = 86
    REDUCEVENDORPRICES = 87
    DOUBLEHERBDURATION = 88
    LIGHTRADIUS = 89
    LIGHTCOLOUR = 90
    REDUCEDREQUIREMENTS = 91
    REDUCEDLEVELREQ = 92
    IAS = 93
    REDUCEDLEVELREQPCT = 94
    LASTBLOCKFRAME = 95
    FASTERRUNWALK = 96
    NONCLASSSKILL = 97
    STATE = 98
    FASTERHITRECOVERY = 99
    MONSTERPLAYERCOUNT = 100
    SKILLPOISONOVERRIDELEN = 101
    FASTERBLOCK = 102
    SKILLBYPASSUNDEAD = 103
    SKILLBYPASSDEMONS = 104
    FASTERCAST = 105
    SKILLBYPASSBEASTS = 106
    SINGLESKILL = 107
    SLAINMONSTERSRIP = 108
    CURSERESISTANCE = 109
    POISONLENGTHREDUCTION = 110
    ADDSDAMAGE = 111
    HITCAUSESMONSTERTOFLEE = 112
    HITBLINDSTARGET = 113
    DAMAGETOMANA = 114
    IGNORETARGETSDEFENSE = 115
    REDUCETARGETSDEFENSE = 116
    PREVENTMONSTERHEAL = 117
    HALFFREEZEDURATION = 118
    TOHITPERCENT = 119
    MONSTERDEFDUCTPERHIT = 120
    DAMAGETODEMONS = 121
    DAMAGETOUNDEAD = 122
    ATTACKRATINGVSDEMONS = 123
    ATTACKRATINGVSUNDEAD = 124
    THROWABLE = 125
    ELEMENTALSKILLS = 126
    ALLSKILLS = 127
    ATTACKERTAKESLTNGDMG = 128
    IRONMAIDENLEVEL = 129
    LIFETAPLEVEL = 130
    THORNSPERCENT = 131
    BONEARMOR = 132
    MAXIMUMBONEARMOR = 133
    FREEZESTARGET = 134
    OPENWOUNDS = 135
    CRUSHINGBLOW = 136
    KICKDAMAGE = 137
    MANAAFTEREACHKILL = 138
    LIFEAFTEREACHDEMONKILL = 139
    EXTRABLOOD = 140
    DEADLYSTRIKE = 141
    FIREABSORBPERCENT = 142
    FIREABSORB = 143
    LIGHTNINGABSORBPERCENT = 144
    LIGHTNINGABSORB = 145
    MAGICABSORBPERCENT = 146
    MAGICABSORB = 147
    COLDABSORBPERCENT = 148
    COLDABSORB = 149
    SLOW = 150
    AURA = 151
    INDESTRUCTIBLE = 152
    CANNOTBEFROZEN = 153
    STAMINADRAINPERCENT = 154
    REANIMATE = 155
    PIERCINGATTACK = 156
    FIRESMAGICARROWS = 157
    FIREEXPLOSIVEARROWS = 158
    MINIMUMTHROWINGDAMAGE = 159
    MAXIMUMTHROWINGDAMAGE = 160
    SKILLHANDOFATHENA = 161
    SKILLSTAMINAPERCENT = 162
    SKILLPASSIVESTAMINAPCT = 163
    CONCENTRATION = 164
    ENCHANT = 165
    PIERCE = 166
    CONVICTION = 167
    CHILLINGARMOR = 168
    FRENZY = 169
    DECREPIFY = 170
    SKILLARMORPERCENT = 171
    ALIGNMENT = 172
    TARGET0 = 173
    TARGET1 = 174
    GOLDLOST = 175
    CONVERSIONLEVEL = 176
    CONVERSIONMAXIMUMLIFE = 177
    UNITDOOVERLAY = 178
    ATTACKRTNGVSMONSTERTYPE = 179
    DAMAGETOMONSTERTYPE = 180
    FADE = 181
    ARMOROVERRIDEPERCENT = 182
    UNUSED183 = 183
    UNUSED184 = 184
    UNUSED185 = 185
    UNUSED186 = 186
    UNUSED187 = 187
    SKILLTAB = 188
    UNUSED189 = 189
    UNUSED190 = 190
    UNUSED191 = 191
    UNUSED192 = 192
    UNUSED193 = 193
    SOCKETS = 194
    SKILLONSTRIKING = 195
    SKILLONKILL = 196
    SKILLONDEATH = 197
    SKILLONHIT = 198
    SKILLONLEVELUP = 199
    UNUSED200 = 200
    SKILLWHENSTRUCK = 201
    UNUSED202 = 202
    UNUSED203 = 203
    CHARGED = 204
    UNUSED204 = 205
    UNUSED205 = 206
    UNUSED206 = 207
    UNUSED207 = 208
    UNUSED208 = 209
    UNUSED209 = 210
    UNUSED210 = 211
    UNUSED211 = 212
    UNUSED212 = 213
    DEFENSEPERLEVEL = 214
    ENHANCEDDEFENSEPERLVL = 215
    LIFEPERLEVEL = 216
    MANAPERLEVEL = 217
    MAXDAMAGEPERLEVEL = 218
    MAXENHANCEDDMGPERLEVEL = 219
    STRENGTHPERLEVEL = 220
    DEXTERITYPERLEVEL = 221
    ENERGYPERLEVEL = 222
    VITALITYPERLEVEL = 223
    ATTACKRATINGPERLEVEL = 224
    BONUSATTACKRATINGPERLEVEL = 225
    MAXCOLDDAMAGEPERLEVEL = 226
    MAXFIREDAMAGEPERLEVEL = 227
    MAXLIGHTNINGDAMAGEPERLEVEL = 228
    MAXPOISONDAMAGEPERLEVEL = 229
    COLDRESPERLEVEL = 230
    FIRERESPERLEVEL = 231
    LIGHTNINGRESPERLEVEL = 232
    POISONRESPERLEVEL = 233
    COLDABSORBPERLEVEL = 234
    FIREABSORBPERLEVEL = 235
    LIGHTNINGABSORBPERLEVEL = 236
    POISONABSORBPERLEVEL = 237
    THORNSPERLEVEL = 238
    EXTRAGOLDPERLEVEL = 239
    MAGICFINDPERLEVEL = 240
    STAMINAREGENPERLEVEL = 241
    STAMINAPERLEVEL = 242
    DAMAGETODEMONSPERLEVEL = 243
    DAMAGETOUNDEADPERLEVEL = 244
    ATTACKRATINGVSDEMONSPERLEVEL = 245
    ATTACKRATINGVSUNDEADPERLEVEL = 246
    CRUSHINGBLOWPERLEVEL = 247
    OPENWOUNDSPERLEVEL = 248
    KICKDAMAGEPERLEVEL = 249
    DEADLYSTRIKEPERLEVEL = 250
    FINDGEMSPERLEVEL = 251
    REPAIRSDURABILITY = 252
    REPLENISHESQUANTITY = 253
    INCREASEDSTACKSIZE = 254
    FINDITEM = 255
    SLASHDAMAGE = 256
    SLASHDAMAGEPERCENT = 257
    CRUSHDAMAGE = 258
    CRUSHDAMAGEPERCENT = 259
    THRUSTDAMAGE = 260
    THRUSTDAMAGEPERCENT = 261
    SLASHDAMAGEABSORPTION = 262
    CRUSHDAMAGEABSORPTION = 263
    THRUSTDAMAGEABSORPTION = 264
    SLASHDAMAGEABSORBPCT = 265
    CRUSHDAMAGEABSORBPCT = 266
    THRUSTDAMAGEABSORBPCT = 267
    DEFENSEPERTIME = 268
    ENHANCEDDEFENSEPERTIME = 269
    LIFEPERTIME = 270
    MANAPERTIME = 271
    MAXDAMAGEPERTIME = 272
    MAXENHANCEDDMGPERTIME = 273
    STRENGTHPERTIME = 274
    DEXTERITYPERTIME = 275
    ENERGYPERTIME = 276
    VITALITYPERTIME = 277
    ATTACKRATINGPERTIME = 278
    CHANCETOHITPERTIME = 279
    MAXCOLDDAMAGEPERTIME = 280
    MAXFIREDAMAGEPERTIME = 281
    MAXLIGHTNINGDAMAGEPERTIME = 282
    MAXDAMAGEPERPOISON = 283
    COLDRESPERTIME = 284
    FIRERESPERTIME = 285
    LIGHTNINGRESPERTIME = 286
    POISONRESPERTIME = 287
    COLDABSORPTIONPERTIME = 288
    FIREABSORPTIONPERTIME = 289
    LIGHTNINGABSORBPERTIME = 290
    POISONABSORBPERTIME = 291
    EXTRAGOLDPERTIME = 292
    MAGICFINDPERTIME = 293
    REGENSTAMINAPERTIME = 294
    STAMINAPERTIME = 295
    DAMAGETODEMONSPERTIME = 296
    DAMAGETOUNDEADPERTIME = 297
    ATTACKRATINGVSDEMONSPERTIME = 298
    ATTACKRATINGVSUNDEADPERTIME = 299
    CRUSHINGBLOWPERTIME = 300
    OPENWOUNDSPERTIME = 301
    KICKDAMAGEPERTIME = 302
    DEADLYSTRIKEPERTIME = 303
    FINDGEMSPERTIME = 304
    ENEMYCOLDRESREDUCTION = 305
    ENEMYFIRERESREDUCTION = 306
    ENEMYLIGHTRESREDUCTION = 307
    ENEMYPOISONRESREDUCTION = 308
    DAMAGEVSMONSTERS = 309
    ENHANCEDDMGVSMONSTERS = 310
    ATTACKRATINGVSMONSTERS = 311
    BONUSATTACKRATINGVSMONSTERS = 312
    DEFENSEVSMONSTERS = 313
    ENHANCEDDEFVSMONSTERS = 314
    FIREDAMAGELENGTH = 315
    MINFIREDAMAGELENGTH = 316
    MAXFIREDAMAGELENGTH = 317
    PROGRESSIVEDAMAGE = 318
    PROGRESSIVESTEAL = 319
    PROGRESSIVEOTHER = 320
    PROGRESSIVEFIRE = 321
    PROGRESSIVECOLD = 322
    PROGRESSIVELIGHTNING = 323
    EXTRACHARGES = 324
    PROGRESSIVEATTACKRATING = 325
    POISONCOUNT = 326
    DAMAGEFRAMERATE = 327
    PIERCEIDX = 328
    FIREMASTERY = 329
    LIGHTNINGMASTERY = 330
    COLDMASTERY = 331
    POISONMASTERY = 332
    PASSIVE_ENEMYFIRERESREDUC = 333
    PASSIVE_ENEMYLIGHTNINGRESREDUC = 334
    PASSIVE_ENEMYCOLDRESREDUC = 335
    PASSIVE_ENEMYPOISONRESREDUC = 336
    CRITICALSTRIKE = 337
    DODGE = 338
    AVOID = 339
    EVADE = 340
    WARMTH = 341
    MELEEARMASTERY = 342
    MELEEDAMAGEMASTERY = 343
    MELEECRITHITMASTERY = 344
    THROWNWEAPONARMASTERY = 345
    THROWNWEAPONDMGMASTERY = 346
    THROWNCRITHITMASTERY = 347
    WEAPONBLOCK = 348
    SUMMONRESIST = 349
    MODIFIERLISTSKILL = 350
    MODIFIERLISTLEVEL = 351
    LASTSENTLIFEPERCENT = 352
    SOURCEUNITTYPE = 353
    SOURCEUNITID = 354
    SHORTPARAMETER1 = 355
    QUESTITEMDIFFICULTY = 356
    PASSIVEMAGICDMGMASTERY = 357
    PASSIVEMAGICRESREDUC = 358

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

class Item(Unit):
    @property
    def type(self) -> ItemType:
        try:
            return ItemType(game.get_item_code(self.internal_unit.dwTxtFileNo))
        except:
            return ItemType.UNKNOWN

    @property
    def quality(self) -> Quality:
        return Quality(self.internal_unit.pItemDatadwQuality)

    @property
    def position(self) -> Position:
        return Position(
            self.internal_unit.pItemPathdwPosX,
            self.internal_unit.pItemPathdwPosY
        )

    @property
    def stats(self) -> list[Stat]:
        raw_stats = game.get_item_stats(self.internal_unit)
        if raw_stats is None:
            return []

        return [Stat(StatType(stat_index), value) for stat_index, _, value in raw_stats]


#####################################
## functions                       ##
#####################################
def pick_up(item: Item) -> None:
    game.pick_up(item.id, 4)

def get_player() -> Character:
    return Character(game.get_player_unit())

def get_all_items() -> list[Item]:
    results: list[Item] = []
    for unit in game.get_item_table():
        if not unit or unit.id == 0:
            continue
        results.append(Item(unit))

    return results

def reveal_level() -> None:
    game.reveal_level()


#####################################
## helpers                         ##
#####################################
def write_log(level: str, message: str):
    game.write_log(level, message)

def flex_tick(func):
    game.register_tick(func)
    def wrapper():
        func()
    return wrapper

def distance(begin: Position, end: Position):
    return math.sqrt((begin.x - end.x) ** 2 + (begin.y - end.y) ** 2)