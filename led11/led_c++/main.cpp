#include <stdio.h>
#include <stdlib.h>
#include <deque>
#include "global.h"
#include "log.h"


Setting g_setting;
rgb_matrix::FrameCanvas *g_canvas;
RGBMatrix *g_matrix;

void sig_handler(int signo)
{
    if (SIGINT == signo || SIGTERM == signo)
    {
        Log(critical, "signal(%s) --> App exit", (signo == SIGINT) ? "Ctrl + C" : "Kill command");
        g_setting.end = 1;
    }
}



int main(int argc, char *argv[]) {
    RGBMatrix::Options matrix_options;
    rgb_matrix::RuntimeOptions runtime_opt;
    set_log_level(info);
    set_file_output(false);

    int opt;
    while ((opt = getopt(argc, argv, "p:")) != -1) {
        switch (opt) {
        case 'p':
            g_setting.net_port = atoi(optarg);
            Log(info, "UDP Port:%d", g_setting.net_port);
            break;
        default:
            return rpi_led_usage();
        }
    }  
    // sys_config_out();
    // rpi_led_usage();

    struct sigaction act;
    act.sa_handler = sig_handler;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
    sigaction(SIGINT, &act, NULL);
    sigaction(SIGTERM, &act, NULL);

    matrix_options.cols = 128;
    matrix_options.rows = 64;
    matrix_options.parallel = 3;
    matrix_options.chain_length  = 2;
    matrix_options.show_refresh_rate = 0;
    matrix_options.pwm_bits = 10;
    matrix_options.pwm_dither_bits = 1;
    matrix_options.hardware_mapping = "regular";  //I'm using Electrodragon HAT
    matrix_options.pixel_mapper_config = "V-mapper";  
    
    runtime_opt.gpio_slowdown = 4;


    g_matrix = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
    g_canvas = g_matrix->CreateFrameCanvas();
    pthread_mutex_init(&g_setting.display_mutex, NULL);


    init_net();
    start_net_thread();
    uint8_t *buf;
    while(0 == g_setting.end){
        if (0 == THREAD_USE){
            net_rcv_thread(NULL);
        }
        else{
            buf = get_queue();
            if(buf){
                set_display(buf);
                free(buf);
            }
            else{
                usleep(1000);
            }
        
        }
    }
    Log(critical, "process end ");
    sleep(1);

}

