#include <windows.h>
#include <stdio.h>
#include <Python.h>

#include "api/api.h"
#include "utilities/log.h"
#include "diablo/diablo.h"

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
    PrintGameString(L"flex by pianka", 0);
    PrintGameString(L"version 0.1 (Warnet 2025)", 0);
}

DWORD WINAPI ConsoleThread(LPVOID lpParam) {
    AllocConsole();
    freopen("CONOUT$", "w", stdout);
    freopen("CONOUT$", "w", stderr);
    freopen("CONIN$", "r", stdin);

    print_art();
    write_log("INF","version 0.1 (Warnet 2025)");
    write_log("INF","screen dimensions %ix%i", *screen_width, *screen_height);
    write_log("INF","character %s", GetPlayerUnit()->pPlayerData->szName);
    // load_plugins();

    Py_Initialize();
    PyRun_SimpleString("print('Python says:', 2 + 2)");
    Py_Finalize();

    while (1) {
        Sleep(16);
    }
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
