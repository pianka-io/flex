#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <windows.h>
#include <wingdi.h>
#include <string.h>
#include "hooks.h"
#include "diablo.h"
#include "../utilities/log.h"

#define INST_INT3	0xCC
#define INST_CALL	0xE8
#define INST_NOP	0x90
#define INST_JMP	0xE9
#define INST_RET	0xC3

uint8_t WriteBytes(void *addr, void *data, uint32_t len) {
    uint32_t old_protect;

    if (!VirtualProtect(addr, len, PAGE_READWRITE, (PDWORD)&old_protect)) {
        return 0;
    }

    memcpy(addr, data, len);
    return VirtualProtect(addr, len, old_protect, (PDWORD)&old_protect);
}

void InterceptLocalCode(uint8_t bInst, uint32_t pAddr, uint32_t pFunc, uint32_t dwLen) {
    uint8_t *bCode = (uint8_t *)malloc(dwLen);
    if (!bCode) return;

    memset(bCode, 0x90, dwLen);
    uint32_t dwFunc = pFunc - (pAddr + 5);

    bCode[0] = bInst;
    *(uint32_t *)&bCode[1] = dwFunc;

    WriteBytes((void *)pAddr, bCode, dwLen);
    free(bCode);
}

void PatchJmp(uint32_t dwAddr, uint32_t dwFunc, uint32_t dwLen)
{
    InterceptLocalCode(INST_JMP, dwAddr, dwFunc, dwLen);
}

wchar_t* AnsiToUnicode(const char* str) {
    int len = MultiByteToWideChar(CP_ACP, 0, str, -1, NULL, 0);
    wchar_t* buf = (wchar_t*)malloc(len * sizeof(wchar_t));
    if (buf) {
        MultiByteToWideChar(CP_ACP, 0, str, -1, buf, len);
    }
    return buf;
}

POINT CalculateTextLen(const char* szwText, int Font) {
    POINT ret = {0, 0};

    if (!szwText)
        return ret;

    wchar_t* Buffer = AnsiToUnicode(szwText);
    if (!Buffer)
        return ret;

    uint32_t dwWidth, dwFileNo;
    uint32_t dwOldSize = SetTextSize(Font);
    ret.y = (long)GetTextSize(Buffer, (uintptr_t)&dwWidth, &dwFileNo);
    ret.x = (long)dwWidth;
    SetTextSize(dwOldSize);

    free(Buffer);
    return ret;
}

struct CellFile *myInitCellFile(struct CellFile *cf)
{
    if(cf)
        InitCellFile(cf, &cf, "?", 0, (DWORD)-1, "?");
    return cf;
}

HANDLE OpenFileRead(char *filename)
{
    return CreateFile(filename, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
}

uint8_t *AllocReadFile(const char *filename, size_t *filesize) {
    HANDLE hFile = CreateFile(filename, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        return NULL;
    }

    DWORD size = GetFileSize(hFile, NULL);
    if (size == INVALID_FILE_SIZE || size == 0) {
        CloseHandle(hFile);
        return NULL;
    }

    uint8_t *buffer = malloc(size);
    if (!buffer) {
        CloseHandle(hFile);
        return NULL;
    }

    DWORD bytesRead;
    if (!ReadFile(hFile, buffer, size, &bytesRead, NULL) || bytesRead != size) {
        free(buffer);
        CloseHandle(hFile);
        return NULL;
    }

    CloseHandle(hFile);
    *filesize = size;
    return buffer;
}

struct CellFile *LoadBmpCellFileEx(uint8_t *buf1, int width, int height) {
    uint8_t *buf2 = malloc((width * height * 2) + height);
    if (!buf2) return NULL;

    uint8_t *dest = buf2;
    for (int i = 0; i < height; i++) {
        uint8_t *src = buf1 + (i * ((width + 3) & -4));
        uint8_t *limit = src + width;
        while (src < limit) {
            uint8_t *start = src;
            uint8_t *limit2 = (limit - src > 0x7f) ? src + 0x7f : limit;
            uint8_t trans = !*src;
            do {
                src++;
            } while ((trans == (uint8_t) !*src) && (src < limit2));

            if (!trans || (src < limit)) *dest++ = (uint8_t) ((trans ? 0x80 : 0) + (src - start));
            if (!trans) while (start < src) *dest++ = *start++;
        }
        *dest++ = 0x80;
    }

    uint32_t dc6head[] = {
        6, 1, 0, 0xEEEEEEEE, 1, 1, 0x1C, 0,
        (uint32_t) -1, (uint32_t) -1, 0, 0, 0, (uint32_t) -1, (uint32_t) -1
    };

    dc6head[8] = width;
    dc6head[9] = height;
    dc6head[14] = dest - buf2;
    dc6head[13] = sizeof(dc6head) + dc6head[14] + 3;

    uint8_t *ret = malloc(dc6head[13]);
    if (!ret) {
        free(buf2);
        return NULL;
    }

    memcpy(ret, dc6head, sizeof(dc6head));
    memcpy(ret + sizeof(dc6head), buf2, dc6head[14]);
    memset(ret + sizeof(dc6head) + dc6head[14], 0xEE, 3);

    free(buf2);

    return (struct CellFile *) ret;
}

struct CellFile *LoadBmpCellFile(char *filename) {
    uint8_t *ret = NULL;
    size_t filesize = 0;  // Store file size

    uint8_t *buf1 = AllocReadFile(filename, &filesize);
    if (!buf1) {
        write_log("ERR", "Failed to read file: %s", filename);
        return NULL;
    }

    BITMAPFILEHEADER *bmphead1 = (BITMAPFILEHEADER *)buf1;
    BITMAPINFOHEADER *bmphead2 = (BITMAPINFOHEADER *)(buf1 + sizeof(BITMAPFILEHEADER));

    if (bmphead1->bfType != 0x4D42) {
        write_log("ERR", "Invalid BMP signature in file: %s", filename);
        free(buf1);
        return NULL;
    }

    if (bmphead2->biBitCount != 8 || bmphead2->biCompression != BI_RGB) {
        write_log("ERR", "Unsupported BMP format (bit depth: %d, compression: %d) in file: %s",
                  bmphead2->biBitCount, bmphead2->biCompression, filename);
        free(buf1);
        return NULL;
    }

    if (bmphead1->bfOffBits > filesize) {
        write_log("ERR", "Invalid bfOffBits in BMP file: %s", filename);
        free(buf1);
        return NULL;
    }

    ret = (uint8_t *)LoadBmpCellFileEx(buf1 + bmphead1->bfOffBits, bmphead2->biWidth, bmphead2->biHeight);
    if (!ret) {
        write_log("ERR", "LoadBmpCellFileEx failed for: %s", filename);
    }

    free(buf1);
    return (struct CellFile *)ret;
}

#define MAX_CACHE_SIZE 128

struct CacheEntry {
    char path[MAX_PATH];
    struct CellFile* cellFile;
};

static struct CacheEntry cache[MAX_CACHE_SIZE];
static size_t cache_count = 0;

struct CellFile* LoadCellFile(char* lpszPath) {
    for (size_t i = 0; i < cache_count; i++) {
        if (strcmp(cache[i].path, lpszPath) == 0) {
            return cache[i].cellFile;
        }
    }

    FILE* file = fopen(lpszPath, "rb");
    if (file) {
        fclose(file);
        struct CellFile* cellFile = myInitCellFile(LoadBmpCellFile(lpszPath));
        if (!cellFile) {
            write_log("ERR", "LoadBmpCellFile failed for: %s", lpszPath);
            return NULL;
        }

        if (cache_count < MAX_CACHE_SIZE) {
            strncpy(cache[cache_count].path, lpszPath, MAX_PATH);
            cache[cache_count].cellFile = cellFile;
            cache_count++;
        }

        return cellFile;
    }
    return NULL;
}

void myDrawAutomapCell(struct CellFile *cellfile, int xpos, int ypos, uint8_t col) {
    if (!cellfile) return;

    struct CellContext ct;
    memset(&ct, 0, sizeof(ct));
    ct.pCellFile = cellfile;

    xpos -= (cellfile->cells[0]->width / 2);
    ypos += (cellfile->cells[0]->height / 2);

    int xpos2 = xpos - cellfile->cells[0]->xoffs;
    int ypos2 = ypos - cellfile->cells[0]->yoffs;

    if ((xpos2 >= *screen_width) || ((xpos2 + (int)cellfile->cells[0]->width) <= 0) ||
        (ypos2 >= *screen_height) || ((ypos2 + (int)cellfile->cells[0]->height) <= 0)) {
        return;
        }

    static uint8_t coltab[2][256];

    if (!coltab[0][1]) {
        for (int k = 0; k < 255; k++) {
            coltab[0][k] = (uint8_t)k;
            coltab[1][k] = (uint8_t)k;
        }
    }

    cellfile->mylastcol = coltab[cellfile->mytabno ^= (col != cellfile->mylastcol)][255] = col;

    DrawAutomapCell2(&ct, xpos, ypos, (uint32_t)-1, 5, coltab[cellfile->mytabno]);
}

void myDrawText(const char* szwText, int x, int y, int color, int font) {
    wchar_t* text = AnsiToUnicode(szwText);
    if (!text) return;

    size_t len = strlen(szwText);
    for (size_t i = 0; i < len; i++) {
        if ((unsigned char)szwText[i] == 0xFF) {
            text[i] = 0xFF;
        }
    }

    uint32_t dwOld = SetTextSize(font);
    DrawTextEx2(text, x, y, color, 0);
    SetTextSize(dwOld);

    free(text);
}

void DrawLogo(void) {
    static char image[] = "resources\\name.bmp";
    static char version[] = "\xFF" "c0flex by pianka";

    int x = 0;
    if (version[0] != '\0') {
        POINT textSize = CalculateTextLen(version, 0);
        x = textSize.x / 2;
    }

    struct CellFile* vimg = LoadCellFile(image);
    uint32_t dx = (*screen_width / 2);

    myDrawAutomapCell(vimg, dx, 12, 0);
    myDrawText(version, dx - x, 18, 4, 0);
}

void GameDraw() {
    DrawLogo();
}

void __declspec(naked) GameDraw_Interception()
{
    __asm
    {
        call GameDraw;
        pop esi
        pop ebx
        pop ecx
        retn 4
    }
}

void hook() {
    HMODULE d2client = GetModuleHandleA("D2Client.dll");
    PatchJmp((uintptr_t)d2client + 0xC3DB4, GameDraw_Interception, 6);
}
