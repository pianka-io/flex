#ifndef FLEXLIB_HOOKS_H
#define FLEXLIB_HOOKS_H

void hook();
wchar_t* AnsiToUnicode(const char* str);
char* UnicodeToAnsi(const wchar_t* str);

#endif