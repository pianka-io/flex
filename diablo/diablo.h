#ifndef FLEXLIB_D2_H
#define FLEXLIB_D2_H

#include <stdbool.h>
#include <stdint.h>
#include <wchar.h>
#include "structs.h"

typedef void(__stdcall *PrintGameString_t)(wchar_t *wMessage, int nColor);
typedef uint32_t(__stdcall *GetMouseXOffset_t)(void);
typedef uint32_t(__stdcall *GetMouseYOffset_t)(void);
typedef uint8_t(__stdcall *GetGameDifficulty_t)(void);
typedef uint8_t(__stdcall *ExitGame_t)(void);
typedef struct UnitAny *(__stdcall *GetPlayerUnit_t)(void);
typedef uint32_t(__stdcall *GetUnitX_t)(struct UnitAny* unit);
typedef uint32_t(__stdcall *GetUnitY_t)(struct UnitAny* unit);
typedef void(__stdcall *SendPacket_t)(size_t len, uint32_t unknown, uint8_t *data);

extern uint32_t *screen_width;
extern uint32_t *screen_height;

extern uint32_t *mouse_x;
extern uint32_t *mouse_y;

extern uint32_t *automap_open;

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
bool Interact(uint32_t unit_id, uint32_t unit_type);

#endif
