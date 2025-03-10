#include <windows.h>
#include "constants.h"
#include "diablo.h"

#include <stdbool.h>

uint32_t *screen_width;
uint32_t *screen_height;

uint32_t *mouse_x;
uint32_t *mouse_y;

uint32_t *automap_open;
uint32_t *difficulty;

PrintGameString_t PrintGameString = NULL;
GetMouseXOffset_t GetMouseXOffset = NULL;
GetMouseYOffset_t GetMouseYOffset = NULL;
GetGameDifficulty_t GetGameDifficulty = NULL;
ExitGame_t ExitGame = NULL;
GetPlayerUnit_t GetPlayerUnit = NULL;
GetUnitX_t GetUnitX = NULL;
GetUnitY_t GetUnitY = NULL;
SendPacket_t SendPacket = NULL;

struct UnitAny **PlayerTable = NULL;
struct UnitAny **MonsterTable = NULL;
struct UnitAny **ObjectTable = NULL;
struct UnitAny **MissileTable = NULL;
struct UnitAny **ItemTable = NULL;
struct UnitAny **TileTable = NULL;

void Initialize() {
    HMODULE d2client = GetModuleHandleA("D2Client.dll");
    HMODULE d2net = GetModuleHandleA("D2Net.dll");
    if (!d2client) {
        return;
    }

    screen_width = (uint32_t *)((uintptr_t)d2client + 0xDBC48);
    screen_height = (uint32_t *)((uintptr_t)d2client + 0xDBC4C);

    mouse_x = (uint32_t *)((uintptr_t)d2client + 0x11B828);
    mouse_y = (uint32_t *)((uintptr_t)d2client + 0x11B824);

    automap_open = (uint32_t *)((uintptr_t)d2client + 0x11B9AC);
    difficulty = (uint32_t *)((uintptr_t)d2client + 0x11C390);

    /* functions */
    PrintGameString = (PrintGameString_t)((uintptr_t)d2client + 0x7D850);
    GetMouseXOffset = (GetMouseXOffset_t)((uintptr_t)d2client + 0x15FB0);
    GetMouseYOffset = (GetMouseYOffset_t)((uintptr_t)d2client + 0x15FA0);
    GetGameDifficulty = (GetGameDifficulty_t)((uintptr_t)d2client + 0x41930);
    ExitGame = (ExitGame_t)((uintptr_t)d2client + 0x42850);
    GetPlayerUnit = (GetPlayerUnit_t)((uintptr_t)d2client + 0xA4D70);
    GetUnitX = (GetUnitX_t)((uintptr_t)d2client + 0x1630);
    GetUnitY = (GetUnitY_t)((uintptr_t)d2client + 0x1660);
    SendPacket = (SendPacket_t)((uintptr_t)d2net + 0x7650);

    /* tables */
    uintptr_t unit_table_base = (uintptr_t)d2client + 0x10A608;
    struct UnitAny **unit_table = (struct UnitAny **)unit_table_base;
    PlayerTable  = &unit_table[128 * UNIT_PLAYER];
    MonsterTable = &unit_table[128 * UNIT_MONSTER];
    ObjectTable  = &unit_table[128 * UNIT_OBJECT];
    MissileTable = &unit_table[128 * UNIT_MISSILE];
    ItemTable    = &unit_table[128 * UNIT_ITEM];
    TileTable    = &unit_table[128 * UNIT_TILE];
}

bool Interact(uint32_t unit_id, uint32_t unit_type) {
    uint8_t *packet = malloc(13);
    if (!packet) return 0;

    packet[0] = 0x16;
    *(uint32_t *)&packet[1] = unit_type;
    *(uint32_t *)&packet[5] = unit_id;
    *(uint32_t *)&packet[9] = 0x01;

    SendPacket(13, 1, packet);
    free(packet);
    return 1;
}