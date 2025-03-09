#include <windows.h>
#include "diablo.h"

uint32_t *screen_width;
uint32_t *screen_height;

uint32_t *mouse_x;
uint32_t *mouse_y;

uint32_t *automap_open;

PrintGameString_t PrintGameString = NULL;
GetMouseXOffset_t GetMouseXOffset = NULL;
GetMouseYOffset_t GetMouseYOffset = NULL;
GetGameDifficulty_t GetGameDifficulty = NULL;

void Initialize() {
    HMODULE hD2Client = GetModuleHandleA("D2Client.dll");
    if (!hD2Client) {
        return;
    }

    screen_width = (uint32_t *)((uintptr_t)hD2Client + 0xDBC48);
    screen_height = (uint32_t *)((uintptr_t)hD2Client + 0xDBC4C);

    mouse_x = (uint32_t *)((uintptr_t)hD2Client + 0x11B828);
    mouse_y = (uint32_t *)((uintptr_t)hD2Client + 0x11B824);

    automap_open = (uint32_t *)((uintptr_t)hD2Client + 0x11B9Ac);

    PrintGameString = (PrintGameString_t)((BYTE *)hD2Client + 0x7D850);
    GetMouseXOffset = (GetMouseXOffset_t)((BYTE *)hD2Client + 0x15FB0);
    GetMouseYOffset = (GetMouseYOffset_t)((BYTE *)hD2Client + 0x15FA0);
    GetGameDifficulty = (GetGameDifficulty_t)((BYTE *)hD2Client + 0x41930);
}
