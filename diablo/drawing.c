#include <windows.h>
#include "drawing.h"

#include "diablo.h"
#include "hooks.h"
#include "../utilities/log.h"

void world_to_automap(POINT* ptPos, uint32_t x, uint32_t y) {
    int map_x = x * 32;
    int map_y = y * 32;

    if (!automap_divisor || !*automap_divisor || !automap_offset) {
        ptPos->x = ptPos->y = 0;
        return;
    }

    int divisor = *(int*)automap_divisor;
    POINT offset = *automap_offset;

    ptPos->x = ((map_x - map_y) / 2 / divisor) - offset.x + 8;
    ptPos->y = ((map_x + map_y) / 4 / divisor) - offset.y - 8;

    if (GetAutomapSize()) {
        --ptPos->x;
        ptPos->y += 5;
    }
}

void draw_automap_text(const struct Element *element) {
    wchar_t* wString = AnsiToUnicode(element->text);
    DWORD oldFont = SetTextSize(0);
    POINT point;
    world_to_automap(&point, element->x1, element->y1);
    DrawTextEx2(wString, point.x, point.y, element->color, 0);
    SetTextSize(oldFont);
    free(wString);
}

void draw_automap_line(const struct Element *element) {
    POINT p1, p2;
    world_to_automap(&p1, element->x1, element->y1);
    world_to_automap(&p2, element->x2, element->y2);
    DrawLine(p1.x, p1.y, p2.x, p2.y, element->color, -1);
}

void draw_automap_cross(const struct Element *element) {
    POINT point;
    world_to_automap(&point, element->x1, element->y1);
    CHAR szLines[][2] = {0,-2, 4,-4, 8,-2, 4,0, 8,2, 4,4, 0,2, -4,4, -8,2, -4,0, -8,-2, -4,-4, 0,-2};
    for (int x = 0; x < 12; x++) {
        DrawLine(
            point.x + szLines[x][0],
            point.y + szLines[x][1],
            point.x + szLines[x+1][0],
            point.y + szLines[x+1][1],
            element->color, -1
        );
    }
}

void draw_automap(struct Element *element) {
    if (element == NULL) return;

    switch (element->type) {
        case TEXT_ELEMENT:
            draw_automap_text(element);
            break;
        case LINE_ELEMENT:
            draw_automap_line(element);
            break;
        case CROSS_ELEMENT:
            draw_automap_cross(element);
            break;
        default:
            // write_log("WRN", "Unknown element type %i", element->type);
            break;
    }
}