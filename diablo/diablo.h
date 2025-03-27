#ifndef FLEXLIB_D2_H
#define FLEXLIB_D2_H

#include <stdbool.h>
#include <stdint.h>
#include "structs.h"

/* memory */
extern uint32_t *exp_char_flag;
extern uint32_t *load_act_1;
extern uint32_t *load_act_2;
extern uint32_t *screen_width;
extern uint32_t *screen_height;
extern uint32_t *mouse_x;
extern uint32_t *mouse_y;
extern uint32_t *automap_open;
extern struct AutomapLayer **automap_layer;
extern struct GameInfo **game_info;
extern uint32_t *automap_divisor;
extern POINT *automap_offset;
extern struct Control *first_control;

/* prototypes */
typedef void(__stdcall *PrintGameString_t)(wchar_t *wMessage, int nColor);
typedef uint32_t(__stdcall *GetMouseXOffset_t)(void);
typedef uint32_t(__stdcall *GetMouseYOffset_t)(void);
typedef uint8_t(__stdcall *GetGameDifficulty_t)(void);
typedef uint8_t(__stdcall *ExitGame_t)(void);
typedef struct UnitAny *(__stdcall *GetPlayerUnit_t)(void);
typedef uint32_t(__stdcall *GetUnitX_t)(struct UnitAny* unit);
typedef uint32_t(__stdcall *GetUnitY_t)(struct UnitAny* unit);
typedef void(__stdcall *SendPacket_t)(size_t len, uint32_t unknown, uint8_t *data);
typedef uint32_t(__fastcall *GetTextSize_t)(wchar_t *text, size_t len, uint32_t *unknown);
typedef uint32_t(__fastcall *SetTextSize_t)(size_t size);
typedef void(__stdcall *InitCellFile_t)(void *cellfile, struct CellFile **outptr, char *srcfile, uint32_t lineno, uint32_t filever, uint8_t *filename);
typedef void(__stdcall *DrawAutomapCell2_t)(struct CellContext* context, uint32_t xpos, uint32_t ypos, uint32_t bright2, uint32_t bright, uint8_t *coltab);
typedef void(__fastcall *DrawTextEx2_t)(const wchar_t *wStr, uint32_t xPos, uint32_t yPos, uint32_t dwColor, uint32_t dwUnk);
typedef struct ItemText *(__stdcall *GetItemText_t)(uint32_t dwItemNo);
typedef struct StatList *(__stdcall *GetStatList_t)(struct UnitAny* pUnit, uint32_t unknown, uint32_t dwMaxEntries);
typedef uint32_t(__stdcall *CopyStatList_t)(struct StatList* pStatList, struct Stat* pStatArray, uint32_t dwMaxEntries);
typedef void(__stdcall *RevealAutomapRoom_t)(struct Room1 *pRoom1, uint32_t dwClipFlag, struct AutomapLayer *alayer);
typedef struct AutomapLayer *(__fastcall *InitAutomapLayer_I_t)(uint32_t layerNo);
typedef struct AutomapLayer2 *(__fastcall *GetLayer_t)(uint32_t dwLevelNo);
typedef void(__stdcall *AddRoomData_t)(struct Act *ptAct, uint32_t LevelId, uint32_t Xpos, uint32_t Ypos, struct Room1 * pRoom);
typedef void(__stdcall *RemoveRoomData_t)(struct Act *ptAct, uint32_t LevelId, uint32_t Xpos, uint32_t Ypos, struct Room1 * pRoom);
typedef struct ObjectTxt *(__stdcall *GetObjectText_t)(uint32_t objno);
typedef struct AutomapCell *(__fastcall *NewAutomapCell_t)(void);
typedef void(__fastcall *AddAutomapCell_t)(struct AutomapCell *aCell, struct AutomapCell **node);
typedef struct Act *(__stdcall *LoadAct_t)(uint32_t ActNumber, uint32_t MapId, uint32_t Unk, uint32_t Unk_2, uint32_t Unk_3, uint32_t Unk_4, uint32_t TownLevelId, void *Func_1, void *Func_2);
typedef uint8_t(__stdcall *GetDifficulty_t)(void);
typedef void(__stdcall *InitLevel_t)(struct Level *pLevel);
typedef void(__stdcall *UnloadAct_t)(struct Act *pAct);
typedef struct Level *(__fastcall *GetLevelEx_t)(struct ActMisc *pMisc, uint32_t dwLevelNo);
typedef void(__stdcall *DrawLine_t)(uint32_t x1, uint32_t y1, uint32_t x2, uint32_t y2, uint32_t color, uint32_t unk);
typedef void(__stdcall *AbsScreenToMap_t)(long *pX, long *pY);
typedef void(__stdcall *MapToAbsScreen_t)(long *pX, long *pY);
typedef uint32_t(__stdcall *GetAutomapSize_t)(void);

/* functions */
extern PrintGameString_t PrintGameString;
extern GetMouseXOffset_t GetMouseXOffset;
extern GetMouseYOffset_t GetMouseYOffset;
extern GetGameDifficulty_t GetGameDifficulty;
extern ExitGame_t ExitGame;
extern GetPlayerUnit_t GetPlayerUnit;
extern GetUnitX_t GetUnitX;
extern GetUnitY_t GetUnitY;
extern SendPacket_t SendPacket;
extern GetTextSize_t GetTextSize;
extern SetTextSize_t SetTextSize;
extern InitCellFile_t InitCellFile;
extern DrawAutomapCell2_t DrawAutomapCell2;
extern DrawTextEx2_t DrawTextEx2;
extern GetItemText_t GetItemText;
extern GetStatList_t GetStatList;
extern CopyStatList_t CopyStatList;
extern RevealAutomapRoom_t RevealAutomapRoom;
extern InitAutomapLayer_I_t InitAutomapLayer_I;
extern GetLayer_t GetLayer;
extern AddRoomData_t AddRoomData;
extern RemoveRoomData_t RemoveRoomData;
extern GetObjectText_t GetObjectText;
extern NewAutomapCell_t NewAutomapCell;
extern AddAutomapCell_t AddAutomapCell;
extern LoadAct_t LoadAct;
extern GetDifficulty_t GetDifficulty;
extern InitLevel_t InitLevel;
extern UnloadAct_t UnloadAct;
extern GetLevelEx_t GetLevelEx;
extern DrawLine_t DrawLine;
extern AbsScreenToMap_t AbsScreenToMap;
extern MapToAbsScreen_t MapToAbsScreen;
extern GetAutomapSize_t GetAutomapSize;

/* tables */
extern struct UnitAny **PlayerTable;
extern struct UnitAny **MonsterTable;
extern struct UnitAny **ObjectTable;
extern struct UnitAny **MissileTable;
extern struct UnitAny **ItemTable;
extern struct UnitAny **TileTable;

/* initialize */
void Initialize();

/* helpers */
void GetItemCodeEx(struct UnitAny* pUnit, char* szBuf);
bool PickUp(uint32_t unit_id, uint32_t unit_type);
void reveal_act(uint32_t act);
void reveal_level(struct Level *level);
void reveal_room(struct Room2* room);
void draw_presets(struct Room2 *pRoom2);

#endif
