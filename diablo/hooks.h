#ifndef FLEXLIB_HOOKS_H
#define FLEXLIB_HOOKS_H

void hook(HMODULE d2client);
wchar_t* AnsiToUnicode(const char* str);
char* UnicodeToAnsi(const wchar_t* str);

#endif