#ifndef FLEX_DRAWING_H
#define FLEX_DRAWING_H

#include <stdint.h>

#define TEXT_ELEMENT 0
#define LINE_ELEMENT 1
#define CROSS_ELEMENT 2

struct Element {
    uint8_t type;
    char text[128];
    uint8_t color;
    uint32_t x1;
    uint32_t y1;
    uint32_t x2;
    uint32_t y2;
};

void draw_automap(struct Element *element);
void world_to_automap(POINT* ptPos, uint32_t x, uint32_t y);

#endif
