#include "api.h"
#include <stdio.h>
#include <windows.h>

#include "log.h"

#define PLUGIN_DIR "C:\\Users\\Rick Pianka\\Code\\flexlib\\cmake-build-debug\\plugins"

Plugin *plugins[MAX_PLUGINS] = {0};  // Now accessible externally
size_t plugin_count = 0;

static event_callback_t global_callbacks[MAX_CALLBACKS] = {0};
static size_t callback_count = 0;
static volatile int running = 1;
static HANDLE tickThread = NULL;

void load_plugins() {
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = FindFirstFile(PLUGIN_DIR "\\*.dll", &findFileData);

    if (hFind == INVALID_HANDLE_VALUE) {
        write_log("ERR", "No plugins found in %s\n", PLUGIN_DIR);
        return;
    }

    do {
        char plugin_path[MAX_PATH];
        snprintf(plugin_path, MAX_PATH, "%s\\%s", PLUGIN_DIR, findFileData.cFileName);

        HMODULE hPlugin = LoadLibrary(plugin_path);
        if (!hPlugin) {
            write_log("ERR", "Failed to load plugin: %s\n", findFileData.cFileName);
            continue;
        }

        Plugin* (*get_plugin)(void) = (Plugin* (*)(void)) GetProcAddress(hPlugin, "get_plugin");
        if (!get_plugin) {
            write_log("ERR", "Invalid plugin (missing get_plugin): %s\n", findFileData.cFileName);
            FreeLibrary(hPlugin);
            continue;
        }

        Plugin* plugin = get_plugin();
        if (plugin) {
            register_plugin(plugin);
        }

        write_log("INF", "Registered plugin %s", findFileData.cFileName);
    } while (FindNextFile(hFind, &findFileData));

    FindClose(hFind);
}

void register_plugin(Plugin *plugin) {
    if (plugin_count < MAX_PLUGINS) {
        plugins[plugin_count++] = plugin;
        if (plugin->init) plugin->init();
    }
}

void unregister_plugin(Plugin *plugin) {
    for (size_t i = 0; i < plugin_count; i++) {
        if (plugins[i] == plugin) {
            if (plugin->shutdown) plugin->shutdown();
            plugins[i] = plugins[--plugin_count];
            break;
        }
    }
}

void register_event_callback(const char *event, event_callback_t callback) {
    if (callback_count < MAX_CALLBACKS) {
        global_callbacks[callback_count++] = callback;
    }
}

void dispatch_event(const char *event, void *data) {
    for (size_t i = 0; i < callback_count; i++) {
        if (global_callbacks[i]) global_callbacks[i](event, data);
    }
}

DWORD WINAPI tick_thread(LPVOID param) {
    while (running) {
        for (size_t i = 0; i < plugin_count; i++) {
            if (plugins[i] && plugins[i]->tick) {
                plugins[i]->tick();
            }
        }
        Sleep(10);
    }
    return 0;
}

void start_tick_loop() {
    if (tickThread) return;
    running = 1;
    tickThread = CreateThread(NULL, 0, tick_thread, NULL, 0, NULL);
}

void stop_tick_loop() {
    running = 0;
    if (tickThread) {
        WaitForSingleObject(tickThread, INFINITE);
        CloseHandle(tickThread);
        tickThread = NULL;
    }
}
