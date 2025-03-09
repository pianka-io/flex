#include <windows.h>
#include <stdio.h>

#include "log.h"
#include "diablo.h"

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
    log("INF","version 0.1 (Warnet 2025)");
    log("INF","screen dimensions (%i, %i)", *screen_width, *screen_height);

    while (1) {
        Sleep(1000);
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hModule);
            CreateThread(NULL, 0, ConsoleThread, NULL, 0, NULL);
            break;
        case DLL_PROCESS_DETACH:
            log("INF", "flexlib.dll detached from process");
            FreeConsole();
            break;
        default:
            break;
    }
    return TRUE;
}
