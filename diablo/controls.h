#ifndef FLEX_CONTROLS_H
#define FLEX_CONTROLS_H

#include <stdint.h>

struct ControlSpace {
  uint32_t pos_x;
  uint32_t pos_y;
  uint32_t size_x;
  uint32_t size_y;
};

struct Control* find_control(int Type, int LocaleID, int Disabled, struct ControlSpace* ControlSpace);

const struct ControlSpace BattleNetButton = { .pos_x = 264, .pos_y = 366, .size_x = 272, .size_y = 35 };

#endif