#include <windows.h>
#include <stdio.h>
#include <Python.h>
#include "library.h"
#include "api/api.h"
#include "utilities/log.h"
#include "diablo/diablo.h"
#include "utilities/list.h"

struct List *plugins = NULL;
CRITICAL_SECTION plugins_lock;

void print_art() {
    printf("________/\\\\\\\\\\__/\\\\\\\\\\\\_________________________________        \n");
    printf(" ______/\\\\\\///__\\////\\\\\\_________________________________       \n");
    printf("  _____/\\\\\\_________\\/\\\\\\_________________________________      \n");
    printf("   __/\\\\\\\\\\\\\\\\\\______\\/\\\\\\________/\\\\\\\\\\\\\\\\___/\\\\\\____/\\\\\\_     \n");
    printf("    _\\////\\\\\\//_______\\/\\\\\\______/\\\\\\/////\\\\\\_\\///\\\\\\/\\\\\\/__    \n");
    printf("     ____\\/\\\\\\_________\\/\\\\\\_____/\\\\\\\\\\\\\\\\\\\\\\____\\///\\\\\\/____   \n");
    printf("      ____\\/\\\\\\_________\\/\\\\\\____\\//\\\\///////______/\\\\\\/\\\\\\___  \n");
    printf("       ____\\/\\\\\\_______/\\\\\\\\\\\\\\\\\\__\\//\\\\\\\\\\\\\\\\\\\\__/\\\\\\/\\///\\\\\\_ \n");
    printf("        ____\\///_______\\/////////____\\//////////__\\///____\\///__\n");
    printf("\n");

    Initialize();
}

DWORD WINAPI ConsoleThread(LPVOID lpParam) {
    AllocConsole();
    freopen("CONOUT$", "w", stdout);
    freopen("CONOUT$", "w", stderr);
    freopen("CONIN$", "r", stdin);

    print_art();
    write_log("INF", "version " FLEX_VERSION " by pianka");
    InitializeCriticalSection(&plugins_lock);

    if (PyImport_AppendInittab("game", PyInit_game) == -1) {
        write_log("ERR", "Failed to register Python module 'game'");
        return 1;
    }

    Py_Initialize();

    PyObject *sysPath = PySys_GetObject("path");
    PyList_Append(sysPath, PyUnicode_FromString("scripts"));

    WIN32_FIND_DATAA findData;
    HANDLE hFind = FindFirstFileA(".\\scripts\\*.py", &findData);

    if (hFind == INVALID_HANDLE_VALUE) {
        write_log("ERR", "No Python scripts found in scripts/ directory.");
    } else {
        EnterCriticalSection(&plugins_lock);
        do {
            if (!(findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                if (strcmp(findData.cFileName, "flex.py") == 0) {
                    continue;
                }

                char module_name[MAX_PATH];
                strncpy(module_name, findData.cFileName, strlen(findData.cFileName) - 3);
                module_name[strlen(findData.cFileName) - 3] = '\0';

                PyObject *py_module_name = PyUnicode_FromString(module_name);
                PyObject *module = PyImport_Import(py_module_name);
                Py_DECREF(py_module_name);

                if (!module) {
                    PyErr_Print();
                    write_log("ERR", "Failed to load Python script: %s", findData.cFileName);
                } else {
                    struct Plugin *plugin = malloc(sizeof(struct Plugin));
                    plugin->automap_elements = NULL;
                    list_insert(&plugins, plugin);
                    write_log("INF", "Loaded Python script: %s", findData.cFileName);
                }
                Py_XDECREF(module);
            }
        } while (FindNextFileA(hFind, &findData));
        FindClose(hFind);
        LeaveCriticalSection(&plugins_lock);
    }

    while (1) {
        flex_loop();
        automap_loop();
    }

    Py_Finalize();
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hModule);
            CreateThread(NULL, 0, ConsoleThread, NULL, 0, NULL);
            break;
        case DLL_PROCESS_DETACH:
            write_log("INF", "flexlib.dll detached from process");
            FreeConsole();
            break;
        default:
            break;
    }
    return TRUE;
}
