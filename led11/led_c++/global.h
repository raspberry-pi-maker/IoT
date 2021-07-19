#pragma once
#include "led-matrix.h"
#include "graphics.h"

#include <ctype.h>
#include <getopt.h>
#include <math.h>
#include <signal.h>
#include <sys/time.h> // for clock_gettime()
#include <termios.h>
#include <unistd.h>
#include <errno.h>
//for int32_t
#include <stdint.h>
#include <list>
using namespace std;
using namespace rgb_matrix;

#define CHUNK_SIZE 50000
#define THREAD_USE 0

typedef struct
{
    int net_port = 4321;     /* protocol version */
    int H = 128, W = 384, C = 3;
    int sock;
    int RCV_BUF = CHUNK_SIZE;
    volatile sig_atomic_t end = 0;
    list<uint8_t *> display_queue;
    pthread_mutex_t display_mutex;

} Setting;

extern Setting g_setting;
extern rgb_matrix::FrameCanvas *g_canvas;
extern RGBMatrix *g_matrix;

int rpi_led_usage();
int sys_config_out();
int init_net();
void start_net_thread();
float calc_FPS(const struct timeval *start, const struct timeval *end);
void set_display(const uint8_t *display);
void *net_rcv_thread(void *data);
void insert_queue(const uint8_t *display);
uint8_t *get_queue();

