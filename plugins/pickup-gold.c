#include <math.h>
#include "../api.h"
#include "../diablo/diablo.h"
#include "../log.h"

static void pickup_gold_tick(void) {
    struct UnitAny *unit = NULL;
    struct UnitAny *player = GetPlayerUnit();
    if (!player || !player->pPath) return;

    uint16_t playerX = player->pPath->xPos;
    uint16_t playerY = player->pPath->yPos;

    for (int bucket = 0; bucket < 128; bucket++) {
        unit = ItemTable[bucket];

        while (unit) {
            if (unit->dwTxtFileNo == 0x20B) {
                uint16_t goldX = unit->pItemPath->dwPosX;
                uint16_t goldY = unit->pItemPath->dwPosY;
                float distance = sqrtf(powf(goldX - playerX, 2) + powf(goldY - playerY, 2));

                uint32_t goldAmount = 0;
                struct StatList *stats = unit->pStats;
                if (stats) {
                    for (int i = 0; i < stats->StatVec.wCount; i++) {
                        if (stats->StatVec.pStats[i].wStatIndex == 0xE) {
                            goldAmount = stats->StatVec.pStats[i].dwStatValue;
                            break;
                        }
                    }
                }

                if (distance <= 5.0f) {
                    Interact(unit->dwUnitId, unit->dwType);
                    write_log("INF", "Picking up %i gold", goldAmount);
                }
            }
            unit = unit->pListNext;
        }
    }
}

static Plugin pickup_gold_plugin = {
    .name = "Pickup Gold",
    .tick = pickup_gold_tick
};

__declspec(dllexport) Plugin* get_plugin() {
    return &pickup_gold_plugin;
}
