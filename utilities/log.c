#include "log.h"

#include <windows.h>
#include <stdio.h>
#include <time.h>

void write_log(const char *level, const char *format, ...) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    printf("[%04d-%02d-%02d+%02d:%02d:%02d] [%s] ",
           t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
           t->tm_hour, t->tm_min, t->tm_sec,
           level);

    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);

    printf("\n");
    _flushall();
}