#include "log.h"
#include "../library.h"

#include <windows.h>
#include <stdio.h>
#include <time.h>
#include <stdarg.h>

//debug_mode

void write_log(const char *level, const char *format, ...) {
    if (_stricmp(level, "DBG") == 0 && !debug_mode)
        return;

    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    char timestamp[32];
    snprintf(timestamp, sizeof(timestamp), "[%04d-%02d-%02d+%02d:%02d:%02d]",
             t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
             t->tm_hour, t->tm_min, t->tm_sec);

    char message[1024];
    va_list args;
    va_start(args, format);
    vsnprintf(message, sizeof(message), format, args);
    va_end(args);

    char log_line[1200];
    snprintf(log_line, sizeof(log_line), "%s [%s] %s\n", timestamp, level, message);

    fputs(log_line, stdout);
    fflush(stdout);

    FILE *file = fopen("flex.log", "a");
    if (file) {
        fputs(log_line, file);
        fflush(file);
        fclose(file);
    }
}
