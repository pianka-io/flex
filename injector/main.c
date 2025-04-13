#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <tchar.h>

BOOL EnableDebugPrivilege() {
    HANDLE hToken;
    TOKEN_PRIVILEGES tkp;

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken)) {
        fprintf(stderr, "[ERR] OpenProcessToken failed: %lu\n", GetLastError());
        return FALSE;
    }

    if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tkp.Privileges[0].Luid)) {
        fprintf(stderr, "[ERR] LookupPrivilegeValue failed: %lu\n", GetLastError());
        CloseHandle(hToken);
        return FALSE;
    }

    tkp.PrivilegeCount = 1;
    tkp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    if (!AdjustTokenPrivileges(hToken, FALSE, &tkp, 0, NULL, NULL)) {
        fprintf(stderr, "[ERR] AdjustTokenPrivileges failed: %lu\n", GetLastError());
        CloseHandle(hToken);
        return FALSE;
    }

    CloseHandle(hToken);
    return TRUE;
}

BOOL InjectDLL(DWORD pid, const wchar_t *dllPath) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        fprintf(stderr, "[ERR] OpenProcess failed: %lu\n", GetLastError());
        return FALSE;
    }

    size_t len = (wcslen(dllPath) + 1) * sizeof(wchar_t);
    LPVOID remoteString = VirtualAllocEx(hProcess, NULL, len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remoteString) {
        fprintf(stderr, "[ERR] VirtualAllocEx failed: %lu\n", GetLastError());
        CloseHandle(hProcess);
        return FALSE;
    }

    if (!WriteProcessMemory(hProcess, remoteString, dllPath, len, NULL)) {
        fprintf(stderr, "[ERR] WriteProcessMemory failed: %lu\n", GetLastError());
        VirtualFreeEx(hProcess, remoteString, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }

    HMODULE hKernel32 = GetModuleHandleW(L"kernel32.dll");
    LPVOID loadLibraryW = GetProcAddress(hKernel32, "LoadLibraryW");

    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)loadLibraryW, remoteString, 0, NULL);
    if (!hThread) {
        fprintf(stderr, "[ERR] CreateRemoteThread failed: %lu\n", GetLastError());
        VirtualFreeEx(hProcess, remoteString, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, remoteString, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    return TRUE;
}

int wmain(int argc, wchar_t *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: injector.exe <PID> <dll>\n");
        return 1;
    }

    DWORD pid = wcstoul(argv[1], NULL, 10);
    if (pid == 0) {
        fprintf(stderr, "[ERR] Invalid PID\n");
        return 1;
    }

    if (!EnableDebugPrivilege()) {
        fprintf(stderr, "[ERR] Failed to enable SeDebugPrivilege\n");
        return 1;
    }

    wprintf(L"[INFO] Injecting: %s\n", argv[2]);
    if (!InjectDLL(pid, argv[2])) {
        fprintf(stderr, "[ERR] Failed to inject dll\n");
        return 1;
    }

    printf("[OK] Injection successful\n");
    return 0;
}
