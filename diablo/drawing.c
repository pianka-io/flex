#include <windows.h>
#include "drawing.h"

#include "diablo.h"
#include "hooks.h"
#include "../utilities/log.h"

void world_to_automap(POINT* ptPos, uint32_t x, uint32_t y) {
    x *= 32; y *= 32;
    ptPos->x = ((x - y)/2/(*(INT*)automap_divisor))-(*automap_offset).x+8;
    ptPos->y = ((x + y)/4/(*(INT*)automap_divisor))-(*automap_offset).y-8;
    if (GetAutomapSize()) {
        --ptPos->x;
        ptPos->y += 5;
    }
}

void draw_automap_text(const struct Element *element) {
    wchar_t* wString = AnsiToUnicode(element->text);

    // if (InRange(*p_D2CLIENT_MouseX, *p_D2CLIENT_MouseY) && GetHoverColor() != Disabled)
    //     drawColor = hoverColor;

    DWORD oldFont = SetTextSize(0);
    POINT point;
    world_to_automap(&point, element->x1, element->y1);
    // DrawText(wString, GetX(), GetY() + GetYSize(), drawColor, 0);
    DrawTextEx2(wString, point.x, point.y, element->color, 0);
    SetTextSize(oldFont);
    free(wString);
}

void draw_automap_line(const struct Element *element) {
	DrawLine(element->x1, element->y1, element->x2, element->y2, element->color, -1);
}

void draw_automap_cross(const struct Element *element) {
    CHAR szLines[][2] = {0,-2, 4,-4, 8,-2, 4,0, 8,2, 4,4, 0,2, -4,4, -8,2, -4,0, -8,-2, -4,-4, 0,-2};
    for (int x = 0; x < 12; x++) {
        DrawLine(
            element->x1 + szLines[x][0],
            element->y1 + szLines[x][1],
            element->x1 + szLines[x+1][0],
            element->y1 + szLines[x+1][1],
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
            write_log("WRN", "Unknown element type %i", element->type);
            break;
    }
}