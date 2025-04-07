#ifndef FLEXLIB_LIBRARY_H
#define FLEXLIB_LIBRARY_H

#include <windows.h>

#define FLEX_VERSION "0.1a"

extern struct List *plugins;
extern CRITICAL_SECTION plugins_lock;
extern boolean debug_mode;
extern struct List *global_automap_elements;

struct Plugin {
    struct List *automap_elements;
};

#endif