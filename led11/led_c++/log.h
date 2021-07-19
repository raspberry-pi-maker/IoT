#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <pthread.h>
#include <errno.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>
#include <iostream>
#include <string>
#include <time.h>
#include <fcntl.h>



#define LOG_PATH  "/var/log"

enum log_level {
    debug = 0,
    info,
    notice,
    warning,
    err,
    critical,
    file_only
};

extern log_level g_log_level;
extern bool g_file_log;

void Log(log_level level, const char * szFormat, ...);
void set_log_level(log_level val);
void set_file_output(bool val);
