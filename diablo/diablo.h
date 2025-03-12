#ifndef FLEXLIB_D2_H
#define FLEXLIB_D2_H

#include <stdbool.h>
#include <stdint.h>
#include "structs.h"

/* memory */
extern uint32_t *screen_width;
extern uint32_t *screen_height;
extern uint32_t *mouse_x;
extern uint32_t *mouse_y;
extern uint32_t *automap_open;

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

#endif
