#ifndef FLEXLIB_D2_H
#define FLEXLIB_D2_H

#include <stdint.h>
#include <wchar.h>

typedef void(__stdcall *PrintGameString_t)(wchar_t *wMessage, int nColor);
typedef uint32_t(__stdcall *GetMouseXOffset_t)(void);
typedef uint32_t(__stdcall *GetMouseYOffset_t)(void);
typedef uint8_t(__stdcall *GetGameDifficulty_t)(void);
typedef uint8_t(__stdcall *ExitGame)(void);

extern uint32_t *screen_width;
extern uint32_t *screen_height;

extern uint32_t *mouse_x;
extern uint32_t *mouse_y;

extern uint32_t *automap_open;

extern PrintGameString_t PrintGameString;
extern GetMouseXOffset_t GetMouseXOffset;
extern GetMouseYOffset_t GetMouseYOffset;
extern GetGameDifficulty_t GetGameDifficulty;

void Initialize();

#endif
