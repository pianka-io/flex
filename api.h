#ifndef FLEXLIB_API_H
#define FLEXLIB_API_H

#include <stddef.h>

#define MAX_PLUGINS 16
#define MAX_CALLBACKS 32

typedef void (*tick_func_t)(void);
typedef void (*event_callback_t)(const char *event, void *data);

typedef struct {
    const char *name;
    void (*init)(void);
    void (*shutdown)(void);
    tick_func_t tick;
    event_callback_t callbacks[MAX_CALLBACKS];
} Plugin;

extern Plugin *plugins[MAX_PLUGINS];
extern size_t plugin_count;

void load_plugins();
void register_plugin(Plugin *plugin);
void unregister_plugin(Plugin *plugin);
void register_event_callback(const char *event, event_callback_t callback);
void dispatch_event(const char *event, void *data);
void start_tick_loop(void);
void stop_tick_loop(void);

#endif
