#include <stdbool.h>
#include <windows.h>
#include "../utilities/log.h"
#include "constants.h"
#include "diablo.h"

#include <corecrt_math.h>

#include "hooks.h"

#pragma optimize("", off)

uint32_t *exp_char_flag = NULL;
uint32_t *load_act_1 = NULL;
uint32_t *load_act_2 = NULL;
uint32_t *screen_width = NULL;
uint32_t *screen_height = NULL;
uint32_t *mouse_x = NULL;
uint32_t *mouse_y = NULL;
uint32_t *automap_open = NULL;
struct AutomapLayer **automap_layer = NULL;
uint32_t *difficulty = NULL;
struct GameInfo **game_info = NULL;
uint32_t *automap_divisor = NULL;
POINT *automap_offset = NULL;
struct Control **first_control = NULL;
struct UnitHashTable *client_side_units = NULL;
struct UnitHashTable *server_side_units = NULL;
uint32_t *viewport_x;
uint32_t *viewport_y;
boolean *always_run;

PrintGameString_t PrintGameString = NULL;
GetMouseXOffset_t GetMouseXOffset = NULL;
GetMouseYOffset_t GetMouseYOffset = NULL;
GetGameDifficulty_t GetGameDifficulty = NULL;
ExitGame_t ExitGame = NULL;
GetPlayerUnit_t GetPlayerUnit = NULL;
GetUnitX_t GetUnitX = NULL;
GetUnitY_t GetUnitY = NULL;
SendPacket_t SendPacket = NULL;
GetTextSize_t GetTextSize = NULL;
SetTextSize_t SetTextSize = NULL;
InitCellFile_t InitCellFile = NULL;
DrawAutomapCell2_t DrawAutomapCell2 = NULL;
DrawTextEx2_t DrawTextEx2 = NULL;
GetItemText_t GetItemText = NULL;
GetStatList_t GetStatList = NULL;
CopyStatList_t CopyStatList = NULL;
RevealAutomapRoom_t RevealAutomapRoom = NULL;
InitAutomapLayer_I_t InitAutomapLayer_I = NULL;
GetLayer_t GetLayer = NULL;
AddRoomData_t AddRoomData = NULL;
RemoveRoomData_t RemoveRoomData = NULL;
GetObjectText_t GetObjectText = NULL;
NewAutomapCell_t NewAutomapCell = NULL;
AddAutomapCell_t AddAutomapCell = NULL;
LoadAct_t LoadAct = NULL;
GetDifficulty_t GetDifficulty = NULL;
InitLevel_t InitLevel = NULL;
UnloadAct_t UnloadAct = NULL;
GetLevelEx_t GetLevelEx = NULL;
DrawLine_t DrawLine = NULL;
AbsScreenToMap_t AbsScreenToMap = NULL;
MapToAbsScreen_t MapToAbsScreen = NULL;
GetAutomapSize_t GetAutomapSize = NULL;
GetHwnd_t GetHwnd = NULL;
SetControlText_t SetControlText = NULL;
GetItemName_t GetItemName = NULL;
GetUnitName_I_t GetUnitName_I = NULL;
SetSelectedUnit_I_t SetSelectedUnit_I = NULL;
ClickMap_t ClickMap = NULL;

struct UnitAny **PlayerTable = NULL;
struct UnitAny **MonsterTable = NULL;
struct UnitAny **ObjectTable = NULL;
struct UnitAny **MissileTable = NULL;
struct UnitAny **ItemTable = NULL;
struct UnitAny **TileTable = NULL;

HMODULE preload_module(const char *name) {
	HMODULE mod = GetModuleHandleA(name);
	if (!mod) {
		mod = LoadLibraryA(name);
	}
	return mod;
}

void initialize_diablo() {
	HMODULE d2common = NULL, d2client = NULL, d2net = NULL;
	HMODULE d2win = NULL, d2gfx = NULL, d2cmp = NULL;

	int retries = 50;
	while (retries-- > 0) {
		d2common = preload_module("d2common.dll");
		d2client = preload_module("d2client.dll");
		d2net    = preload_module("d2net.dll");
		d2win    = preload_module("d2win.dll");
		d2gfx    = preload_module("d2gfx.dll");
		d2cmp    = preload_module("d2cmp.dll");

		if (d2common && d2client && d2net && d2win && d2gfx && d2cmp)
			break;

		Sleep(100);
	}

	if (!d2common) write_log("ERR", "d2common.dll not loaded");
	if (!d2client) write_log("ERR", "d2client.dll not loaded");
	if (!d2net)    write_log("ERR", "d2net.dll not loaded");
	if (!d2win)    write_log("ERR", "d2win.dll not loaded");
	if (!d2gfx)    write_log("ERR", "d2gfx.dll not loaded");
	if (!d2cmp)    write_log("ERR", "d2cmp.dll not loaded");

	if (!d2common || !d2client || !d2net || !d2win || !d2gfx || !d2cmp) {
		write_log("ERR", "One or more required Diablo 2 modules not loaded. Aborting hook setup.");
		return;
	}

	// write_log("DBG", "all diablo modules loaded");

    exp_char_flag = (uint32_t *)((uintptr_t)d2client + 0x119854);
    load_act_1 = (uint32_t *)((uintptr_t)d2client + 0x62AA0);
    load_act_2 = (uint32_t *)((uintptr_t)d2client + 0x62760);
    screen_width = (uint32_t *)((uintptr_t)d2client + 0xDBC48);
    screen_height = (uint32_t *)((uintptr_t)d2client + 0xDBC4C);
    mouse_x = (uint32_t *)((uintptr_t)d2client + 0x11B828);
    mouse_y = (uint32_t *)((uintptr_t)d2client + 0x11B824);
    automap_open = (uint32_t *)((uintptr_t)d2client + 0x11B9AC);
    automap_layer = (struct AutomapLayer **)((uintptr_t)d2client + 0x11C1C4);
    difficulty = (uint32_t *)((uintptr_t)d2client + 0x11C390);
    game_info = (struct GameInfo **)((uintptr_t)d2client + 0x11B980);
    automap_divisor = (uint32_t *)((uintptr_t)d2client + 0xF16B0);
    automap_offset = (POINT *)((uintptr_t)d2client + 0x11C1F8);
    first_control = (struct Control **)((uintptr_t)d2win + 0x214A0);
	client_side_units = (struct UnitHashTable *)((uintptr_t)d2client + 0x109A08);
	server_side_units = (struct UnitHashTable *)((uintptr_t)d2client + 0x10A608);
	viewport_x = (uint32_t *)((uintptr_t)d2client + 0x119960);
	viewport_y = (uint32_t *)((uintptr_t)d2client + 0x11995C);
	always_run = (boolean *)((uintptr_t)d2client + 0x11C3EC);

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
    GetTextSize = (GetTextSize_t)((uintptr_t)d2win + 0x12700);
    SetTextSize = (SetTextSize_t)((uintptr_t)d2win + 0x12FE0);
    InitCellFile = (InitCellFile_t)((uintptr_t)d2cmp + 0x11AC0);
    DrawAutomapCell2 = (DrawAutomapCell2_t)((uintptr_t)d2gfx + 0xB080);
    DrawTextEx2 = (DrawTextEx2_t)((uintptr_t)d2win + 0x12FA0);
    GetItemText = (GetItemText_t)((uintptr_t)d2common + 0x719A0);
    GetStatList = (GetStatList_t)((uintptr_t)d2common + 0x37EC0);
    CopyStatList = (CopyStatList_t)((uintptr_t)d2common + 0x383C0);
    RevealAutomapRoom = (RevealAutomapRoom_t)((uintptr_t)d2client + 0x62580);
    InitAutomapLayer_I = (InitAutomapLayer_I_t)((uintptr_t)d2client + 0x62710);
    GetLayer = (GetLayer_t)((uintptr_t)d2common + 0x6CB20);
    AddRoomData = (AddRoomData_t)((uintptr_t)d2common + 0x3CCA0);
    RemoveRoomData = (RemoveRoomData_t)((uintptr_t)d2common + 0x3CBE0);
    GetObjectText = (GetObjectText_t)((uintptr_t)d2common + 0x3E980);
    NewAutomapCell = (NewAutomapCell_t)((uintptr_t)d2client + 0x5F6B0);
    AddAutomapCell = (AddAutomapCell_t)((uintptr_t)d2client + 0x61320);
    LoadAct = (LoadAct_t)((uintptr_t)d2common + 0x3CB30);
    GetDifficulty = (GetDifficulty_t)((uintptr_t)d2client + 0x41930);
    InitLevel = (InitLevel_t)((uintptr_t)d2common + 0x2E360);
    UnloadAct = (UnloadAct_t)((uintptr_t)d2common + 0x3C990);
    GetLevelEx = (GetLevelEx_t)((uintptr_t)d2common + 0x2D9B0);
    DrawLine = (DrawLine_t)((uintptr_t)d2gfx + 0xB9C0);
    AbsScreenToMap = (AbsScreenToMap_t)((uintptr_t)d2common + 0x3D8E0);
    MapToAbsScreen = (MapToAbsScreen_t)((uintptr_t)d2common + 0x3DB70);
    GetAutomapSize = (GetAutomapSize_t)((uintptr_t)d2client + 0x5F080);
    GetHwnd = (GetHwnd_t)((uintptr_t)d2gfx + 0x7FB0);
    SetControlText = (SetControlText_t)((uintptr_t)d2win + 0x14DF0);
    GetUnitName_I = (GetUnitName_I_t)((uintptr_t)d2client + 0xA5D90);
    GetItemName = (GetItemName_t)((uintptr_t)d2client + 0x914F0);
    SetSelectedUnit_I = (SetSelectedUnit_I_t)((uintptr_t)d2client + 0x51860);
    ClickMap = (ClickMap_t)((uintptr_t)d2client + 0x1BF20);

    /* tables */
    uintptr_t unit_table_base = (uintptr_t)d2client + 0x10A608;
    struct UnitAny **unit_table = (struct UnitAny **)unit_table_base;
    PlayerTable  = &unit_table[128 * UNIT_PLAYER];
    MonsterTable = &unit_table[128 * UNIT_MONSTER];
    ObjectTable  = &unit_table[128 * UNIT_OBJECT];
    MissileTable = &unit_table[128 * UNIT_MISSILE];
    ItemTable    = &unit_table[128 * UNIT_ITEM];
    TileTable    = &unit_table[128 * UNIT_TILE];

    /* hooks */
    hook(d2client);
}

bool send_pick_up_item(uint32_t unit_id, uint32_t unit_type) {
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

void get_item_code(struct UnitAny* pUnit, char* szBuf) {
    if (pUnit->dwType == UNIT_ITEM)
    {
        struct ItemText* pTxt = GetItemText(pUnit->dwTxtFileNo);
        if (pTxt)
        {
            memcpy(szBuf, pTxt->szCode, 3);
            szBuf[3] = 0x00;
        }
    }
}

DWORD __declspec(naked) __fastcall InitAutomapLayer_S(DWORD nLayerNo)
{
    __asm
    {
        push eax;
        mov eax, ecx;
        call InitAutomapLayer_I;
        pop eax;
        ret;
    }
}

DWORD __declspec(naked) __fastcall GetUnitName_S(DWORD UnitAny)
{
	__asm
	{
		mov eax, ecx
		jmp GetUnitName_I
	}
}

void __declspec(naked) __fastcall SetSelectedUnit_S(DWORD UnitAny)
{
	__asm
	{
		mov eax, ecx
		jmp SetSelectedUnit_I
	}
}

struct AutomapLayer *init_layer(uint32_t level) {
    struct AutomapLayer2 *layer = GetLayer(level);

    if (!layer) {
        return false;
    }

    return (struct AutomapLayer *)InitAutomapLayer_S(layer->nLayerNo);
}

wchar_t* get_unit_name(uintptr_t unit) {
	return (wchar_t*)GetUnitName_S(unit);
}

void set_selected_unit(struct UnitAny* unit) {
	SetSelectedUnit_S((uint32_t)unit);
}

struct Level *get_level(struct Act* pAct, uint32_t level) {
	for (struct Level* pLevel = pAct->pMisc->pLevelFirst; pLevel; pLevel = pLevel->pNextLevel)
	{
		if (pLevel->dwLevelNo == level && pLevel->dwPosX > 0)
			return pLevel;
	}
	return GetLevelEx(pAct->pMisc, level);
}

void reveal_act(uint32_t act) {
	struct UnitAny *player = GetPlayerUnit();
	if (!player || !player->pAct)
		return;

	int actIds[6] = {1, 40, 75, 103, 109, 137};
	struct Act* pAct = LoadAct(act - 1, player->pAct->dwMapSeed, *exp_char_flag, 0, GetDifficulty(), NULL, actIds[act - 1], load_act_1, load_act_2);
	if (!pAct || !pAct->pMisc)
		return;

	for (int level = actIds[act - 1]; level < actIds[act]; level++) {
		struct Level* pLevel = get_level(pAct, level);
		if (!pLevel)
			continue;
		if (!pLevel->pRoom2First)
			InitLevel(pLevel);
		reveal_level(pLevel);
	}

	init_layer(player->pPath->pRoom1->pRoom2->pLevel->dwLevelNo);
	UnloadAct(pAct);
}

void reveal_level(struct Level *level) {
    if (level == NULL) return;
    init_layer(level->dwLevelNo);

    for (struct Room2* room = level->pRoom2First; room; room = room->pRoom2Next) {
        bool roomData = false;

        if (!room->pRoom1) {
            AddRoomData(level->pMisc->pAct, level->dwLevelNo, room->dwPosX, room->dwPosY, room->pRoom1);
            roomData = true;
        }

        if (!room->pRoom1)
            continue;

        RevealAutomapRoom(room->pRoom1, TRUE, *automap_layer);

        reveal_room(room);

        // if (roomData) {
        // 	RemoveRoomData(level->pMisc->pAct, level->dwLevelNo, room->dwPosX, room->dwPosY, room->pRoom1);
        // }
    }
}

void reveal_room(struct Room2* room) {
	for (struct PresetUnit* preset = room->pPreset; preset; preset = preset->pPresetNext)
	{
		int cellNo = -1;

		if (preset->dwType == UNIT_MONSTER)
		{
			if (preset->dwTxtFileNo == 256)
				cellNo = 300;
			if (preset->dwTxtFileNo == 745)
				cellNo = 745;
		} else if (preset->dwType == UNIT_OBJECT) {
			if (preset->dwTxtFileNo == 371)
				cellNo = 301;
			else if (preset->dwTxtFileNo == 152)
				cellNo = 300;
			else if (preset->dwTxtFileNo == 460)
				cellNo = 1468;
			if ((preset->dwTxtFileNo == 402) && (room->pLevel->dwLevelNo == 46))
				cellNo = 0;
			if (preset->dwTxtFileNo == 376)
				cellNo = 376;

			if (cellNo == -1 && preset->dwTxtFileNo <= 572) {
				struct ObjectTxt *obj = GetObjectText(preset->dwTxtFileNo);
				if (obj) {
					cellNo = obj->nAutoMap;
				}
			}
		}

		if ((cellNo > 0) && (cellNo < 1258))
		{
			struct AutomapCell* cell = NewAutomapCell();

			cell->nCellNo = cellNo;
			int x = (preset->dwPosX + (room->dwPosX * 5));
			int y = (preset->dwPosY + (room->dwPosY * 5));
			cell->xPixel = (((x - y) * 16) / 10) + 1;
			cell->yPixel = (((y + x) * 8) / 10) - 3;

			AddAutomapCell(cell, &((*automap_layer)->pObjects));
		}
	}
}

void send_mouse_click(uint32_t x, uint32_t y, uint32_t type) {
	HWND hwnd = GetHwnd();
	if (!hwnd) return;

	RECT rect;
	GetClientRect(hwnd, &rect);

	float scale = fminf((float)rect.right / 800.0f, (float)rect.bottom / 600.0f);
	uint32_t viewport_width = (uint32_t)(800 * scale);
	uint32_t viewport_height = (uint32_t)(600 * scale);
	uint32_t offset_x = (rect.right - viewport_width) / 2;
	uint32_t offset_y = (rect.bottom - viewport_height) / 2;

	uint32_t scaled_x = (uint32_t)(x * scale) + offset_x;
	uint32_t scaled_y = (uint32_t)(y * scale) + offset_y;

	LPARAM lp = (scaled_y << 16) | (scaled_x & 0xFFFF);
	PostMessageW(hwnd, type, 0, lp);
}

bool click_control(struct Control *ctrl, uint32_t x, uint32_t y) {
	// if (!ctrl || ClientState() != ClientStateMenu) {
	// 	return false;
	// }

	if (x == -1) {
		x = ctrl->dwPosX + ctrl->dwSizeX / 2;
	}

	if (y == -1) {
		y = ctrl->dwPosY + ctrl->dwSizeY / 2;
	}

	send_mouse_click(x, y, 0);
	Sleep(100);
	send_mouse_click(x, y, 1);
	Sleep(100);

	return true;
}
