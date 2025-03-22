#ifndef FLEXLIB_LIBRARY_H
#define FLEXLIB_LIBRARY_H

#include <windows.h>

#define FLEX_VERSION "0.1a"

extern struct List *plugins;
extern CRITICAL_SECTION plugins_lock;

struct Plugin {
    struct List *automap_elements;
};

#endif