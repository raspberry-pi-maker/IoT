#include "log.h"
#include <stdarg.h>
#include <sys/time.h> // for clock_gettime()
using namespace std;

log_level g_log_level = warning;
bool g_file_log = true;
pthread_mutex_t g_log_mutex = PTHREAD_MUTEX_INITIALIZER;
const char *g_level_msg[] = {
 "[ debug  ]",
 "[  info  ]",
 "[ notice ]",
 "[warning ]",
 "[  err   ]",
 "[critical]",
 "[  file  ]",
 ""
};

const char *g_level_color[] = {
        "\033[1;32;40m",     //Bright Green
        "\033[1;36;40m",     //Bright Cyan 
        "\033[1;35;40m",     //Bright Magenta 
        "\033[1;34;40m",     //Bright Blue
        "\033[1;31;40m",     //Bright Red 
        "\033[1;31;40m",     //Bright Red
        "\033[1;31;40m",     //Bright Red
        "",                  //useless
        ""
};

const char *DEFAULT_COLOR = "\033[1;37;40m";

void Log(log_level level, const char * szFormat, ...)
{
  if(level < g_log_level) return;
  if(level > file_only) return;

  va_list args;
  struct tm *ntime;
  char szPath[256], p[2048], szTime[128];
  timeval curTime;
  FILE *fhLog = NULL;

  gettimeofday(&curTime, NULL);
  ntime = localtime(&curTime.tv_sec);
  sprintf(szTime, "%s [%d/%02d/%02d-%02d:%02d:%02d.%03d]:", g_level_msg[level], ntime->tm_year + 1900, ntime->tm_mon + 1, ntime->tm_mday, ntime->tm_hour, ntime->tm_min, ntime->tm_sec, (int)(curTime.tv_usec/ 1000));
  sprintf(szPath, "%s/rtp_relay_%d%02d%02d.log",  LOG_PATH , ntime->tm_year + 1900, ntime->tm_mon + 1, ntime->tm_mday);

  va_start(args, szFormat);
  vsnprintf (p, sizeof(p), szFormat, args);
  va_end(args) ;

  if(level != file_only) fprintf(stderr, "%s%s%s%s\n", g_level_color[level], g_level_msg[level],DEFAULT_COLOR,  p);

  if(true == g_file_log){
    fhLog = fopen(szPath, "a+");
    if(NULL == fhLog){
    //error  
    fprintf(stderr,  "Log File Path[%s] Not Found\n" , szPath); 
    return;
    }
    //pthread_mutex_lock(&g_log_mutex);
    string str = szTime + (string)p + "\n";
    fwrite(str.c_str(), 1, str.length() + 1, fhLog);
    //pthread_mutex_unlock(&g_log_mutex);
    fclose(fhLog);
    fhLog = NULL;
  }
}

void set_log_level(log_level val)
{
 g_log_level = val;
}

void set_file_output(bool val)
{
  g_file_log = val;
}