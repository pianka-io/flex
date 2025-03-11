#ifndef FLEXLIB_STRUCTS_H
#define FLEXLIB_STRUCTS_H

struct Act;
struct UnitAny;
struct Room1;
struct Room2;
struct Level;

struct QuestInfo {
    void *pBuffer;
    uint32_t _1;
};

struct Waypoint {
    uint8_t flags;
};

struct PlayerData {
    char szName[0x10];
    struct QuestInfo *pNormalQuest;
    struct QuestInfo *pNightmareQuest;
    struct QuestInfo *pHellQuest;
    struct Waypoint *pNormalWaypoint;
    struct Waypoint *pNightmareWaypoint;
    struct Waypoint *pHellWaypoint;
};

struct Inventory {
    uint32_t dwSignature;
    uint8_t *bGame1C;
    struct UnitAny *pOwner;
    struct UnitAny *pFirstItem;
    struct UnitAny *pLastItem;
    uint32_t _1[2];
    uint32_t dwLeftItemUid;
    struct UnitAny *pCursorItem;
    uint32_t dwOwnerId;
    uint32_t dwItemCount;
};

struct ItemData {
    uint32_t dwQuality;
    uint32_t dwSeed[2];
    uint32_t dwItemFlags;
    uint32_t dwFingerPrint;
    uint32_t _1;
    uint32_t dwFlags;
    uint32_t _2[2];
    uint32_t dwActionStamp;
    uint32_t dwFileIndex;
    uint32_t dwItemLevel;
    uint16_t wItemFormat;
    uint16_t wRarePrefix;
    uint16_t wRareSuffix;
    uint16_t wAutoPrefix;
    uint16_t wMagicPrefix[3];
    uint16_t wMagicSuffix[3];
    uint8_t BodyLocation;
    uint8_t ItemLocation;
    uint16_t _4;
    uint8_t bEarLevel;
    uint8_t bInvGfxIdx;
    char szPlayerName[16];
    struct Inventory *pOwnerInventory;
    uint32_t _10;
    struct UnitAny *pNextInvItem;
    uint8_t GameLocation;
    uint8_t NodePage;
    uint16_t _12;
    uint16_t _13[12];
    struct UnitAny *pOwner;
};

struct MonsterData {
    uint8_t _1[22];
    struct
    {
        uint8_t fUnk:1;
        uint8_t fNormal:1;
        uint8_t fChamp:1;
        uint8_t fBoss:1;
        uint8_t fMinion:1;
    };
    uint8_t _2[5];
    uint8_t anEnchants[9];
    uint16_t wUniqueNo;
    uint32_t _5;
    struct {
        wchar_t wName[28];
    };
};

struct ObjectTxt {
    char szName[0x40];
    wchar_t wszName[0x40];
    uint8_t _1[4];
    uint8_t nSelectable0;
    uint8_t _2[0x87];
    uint8_t nOrientation;
    uint8_t _2b[0x19];
    uint8_t nSubClass;
    uint8_t _3[0x11];
    uint8_t nParm0;
    uint8_t _4[0x39];
    uint8_t nPopulateFn;
    uint8_t nOperateFn;
    uint8_t _5[8];
    uint32_t nAutoMap;
};

struct ObjectData {
    struct ObjectTxt *pTxt;
    union {
        uint8_t Type;
        struct {
            uint8_t _1:7;
            uint8_t ChestLocked:1;
        };
    };
    uint32_t _2[8];
    char szOwner[0x10];
};

struct RoomTile {
    struct Room2* pRoom2;
    struct RoomTile* pNext;
    uint32_t _2[2];
    uint32_t *nNum;
};

struct ActMisc {
    uint32_t _1[37];
    uint32_t dwStaffTombLevel;
    uint32_t _2[245];
    struct Act* pAct;
    uint32_t _3[3];
    struct Level* pLevelFirst;
};

struct Level {
    uint32_t _1[4];
    struct Room2* pRoom2First;
    uint32_t _2[2];
    uint32_t dwPosX;
    uint32_t dwPosY;
    uint32_t dwSizeX;
    uint32_t dwSizeY;
    uint32_t _3[96];
    struct Level* pNextLevel;
    uint32_t _4;
    struct ActMisc* pMisc;
    uint32_t _5[6];
    uint32_t dwLevelNo;
    uint32_t _6[3];
    union {
        uint32_t RoomCenterX[9];
        uint32_t WarpX[9];
    };
    union {
        uint32_t RoomCenterY[9];
        uint32_t WarpY[9];
    };
    uint32_t dwRoomEntries;
};

struct PresetUnit {
    uint32_t _1;
    uint32_t dwTxtFileNo;
    uint32_t dwPosX;
    struct PresetUnit* pPresetNext;
    uint32_t _3;
    uint32_t dwType;
    uint32_t dwPosY;
};

struct Room2 {
    uint32_t _1[2];
    struct Room2** pRoom2Near;
    uint32_t _2[5];
    struct {
        uint32_t dwRoomNumber;
        uint32_t _1;
        uint32_t* pdwSubNumber;
    } *pType2Info;
    struct Room2* pRoom2Next;
    uint32_t dwRoomFlags;
    uint32_t dwRoomsNear;
    struct Room1* pRoom1;
    uint32_t dwPosX;
    uint32_t dwPosY;
    uint32_t dwSizeX;
    uint32_t dwSizeY;
    uint32_t _3;
    uint32_t dwPresetType;
    struct RoomTile* pRoomTiles;
    uint32_t _4[2];
    struct Level* pLevel;
    struct PresetUnit* pPreset;
};

struct CollMap {
    uint32_t dwPosGameX;
    uint32_t dwPosGameY;
    uint32_t dwSizeGameX;
    uint32_t dwSizeGameY;
    uint32_t dwPosRoomX;
    uint32_t dwPosRoomY;
    uint32_t dwSizeRoomX;
    uint32_t dwSizeRoomY;
    uint16_t *pMapStart;
    uint16_t *pMapEnd;
};

struct Room1 {
    struct Room1** pRoomsNear;
    uint32_t _1[3];
    struct Room2* pRoom2;
    uint32_t _2[3];
    struct CollMap* Coll;
    uint32_t dwRoomsNear;
    uint32_t _3[9];
    uint32_t dwXStart;
    uint32_t dwYStart;
    uint32_t dwXSize;
    uint32_t dwYSize;
    uint32_t _4[6];
    struct UnitAny* pUnitFirst;
    uint32_t _5;
    struct Room1* pRoomNext;
};

struct Act {
    uint32_t _1[3];
    uint32_t dwMapSeed;
    struct Room1* pRoom1;
    uint32_t dwAct;
    uint32_t _2[12];
    struct ActMisc* pMisc;
};

struct Path {
    uint16_t xOffset;
    uint16_t xPos;
    uint16_t yOffset;
    uint16_t yPos;
    uint32_t _1[2];
    uint16_t xTarget;
    uint16_t yTarget;
    uint32_t _2[2];
    struct Room1 *pRoom1;
    struct Room1 *pRoomUnk;
    uint32_t _3[3];
    struct UnitAny *pUnit;
    uint32_t dwFlags;
    uint32_t _4;
    uint32_t dwPathType;
    uint32_t dwPrevPathType;
    uint32_t dwUnitSize;
    uint32_t _5[4];
    struct UnitAny *pTargetUnit;
    uint32_t dwTargetType;
    uint32_t dwTargetId;
    uint8_t bDirection;
};

struct ItemPath {
    uint32_t _1[3];
    uint32_t dwPosX;
    uint32_t dwPosY;
};

struct ObjectPath {
    struct Room1 *pRoom1;
    uint32_t _1[2];
    uint32_t dwPosX;
    uint32_t dwPosY;
};

struct Stat {
    uint16_t wSubIndex;
    uint16_t wStatIndex;
    uint32_t dwStatValue;
};

struct StatVector {
    struct Stat* pStats;
    uint16_t wCount;
    uint16_t wSize;
};

struct StatList {
    uint32_t _1;
    struct UnitAny* pUnit;
    uint32_t dwUnitType;
    uint32_t dwUnitId;
    uint32_t dwFlags;
    uint32_t _2[4];
    struct StatVector StatVec;
    struct StatList *pPrevLink;
    uint32_t _3;
    struct StatList *pPrev;
    uint32_t _4;
    struct StatList *pNext;
    struct StatList *pSetList;
    uint32_t _5;
    struct StatVector SetStatVec;
    uint32_t _6[2];
    uint32_t StateBits[6];
};

struct Light {
    uint32_t _1[3];
    uint32_t dwType;
    uint32_t _2[7];
    uint32_t dwStaticValid;
    int *pnStaticMap;
};

struct OverheadMsg {
    uint32_t _1;
    uint32_t dwTrigger;
    uint32_t _2[2];
    char Msg[232];
};

struct SkillInfo {
    uint16_t wSkillId;
};

struct Skill {
    struct SkillInfo *pSkillInfo;
    struct Skill *pNextSkill;
    uint32_t _1[8];
    uint32_t dwSkillLevel;
    uint32_t _2[2];
    uint32_t ItemId;
    uint32_t ChargesLeft;
    uint32_t IsCharge;
};

struct Info {
    uint8_t *pGame1C;
    struct Skill *pFirstSkill;
    struct Skill *pLeftSkill;
    struct Skill *pRightSkill;
};

struct UnitAny {
    uint32_t dwType;
    uint32_t dwTxtFileNo;
    uint32_t _1;
    uint32_t dwUnitId;
    uint32_t dwMode;
    union
    {
        struct PlayerData *pPlayerData;
        struct ItemData *pItemData;
        struct MonsterData *pMonsterData;
        struct ObjectData *pObjectData;
    };
    uint32_t dwAct;
    struct Act *pAct;
    uint32_t dwSeed[2];
    uint32_t _2;
    union
    {
        struct Path *pPath;
        struct ItemPath *pItemPath;
        struct ObjectPath *pObjectPath;
    };
    uint32_t _3[5];
    uint32_t dwGfxFrame;
    uint32_t dwFrameRemain;
    uint16_t wFrameRate;
    uint16_t _4;
    uint8_t *pGfxUnk;
    uint32_t *pGfxInfo;
    uint32_t _5;
    struct StatList *pStats;
    struct Inventory *pInventory;
    struct Light *ptLight;
    uint32_t dwStartLightRadius;
    uint16_t nPl2ShiftIdx;
    uint16_t nUpdateType;
    struct UnitAny* pUpdateUnit;
    uint32_t* pQuestRecord;
    uint32_t bSparklyChest;
    uint32_t* pTimerArgs;
    uint32_t dwSoundSync;
    uint32_t _6[2];
    uint16_t wX;
    uint16_t wY;
    uint32_t _7;
    uint32_t dwOwnerType;
    uint32_t dwOwnerId;
    uint32_t _8[2];
    struct OverheadMsg* pOMsg;
    struct Info *pInfo;
    uint32_t _9[6];
    uint32_t dwFlags;
    uint32_t dwFlags2;
    uint32_t _10[5];
    struct UnitAny *pChangedNext;
    struct UnitAny *pListNext;
    struct UnitAny *pRoomNext;
};

struct GfxCell {
    uint32_t flags;
    uint32_t width;
    uint32_t height;
    uint32_t xoffs;
    uint32_t yoffs;
    uint32_t _2;
    uint32_t lpParent;
    uint32_t length;
    uint8_t cols;
};

struct CellFile {
    uint32_t dwVersion;
    struct {
        uint16_t dwFlags;
        uint8_t mylastcol;
        uint8_t mytabno:1;
    };
    uint32_t eFormat;
    uint32_t termination;
    uint32_t numdirs;
    uint32_t numcells;
    struct GfxCell *cells[255];
};

struct CellContext {
    uint32_t _1[13];
    struct CellFile* pCellFile;
    uint32_t _2[4];
};

#endif