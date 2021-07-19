#include <stdio.h>
#include <stdlib.h>

//socket headers
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "global.h"
#include "log.h"

void *net_rcv_thread(void *data);

int rpi_led_usage() {
  rgb_matrix::PrintMatrixFlags(stderr);
  return 1;
}


int sys_config_out()
{
  Log(info, "===== system configuration values =====");
  Log(info, "UDP Port:%d" , g_setting.net_port) ;
  Log(info, "Display H:%d  W:%d C:%d",  g_setting.H, g_setting.W , g_setting.C);
  return 0;
}

/*
Build UDP socket that receives display data from LED server
So this socket shoud be server mode(needs binding). 
*/
int init_net()
{
    struct sockaddr_in srvaddr;

    srvaddr.sin_family = AF_INET;
    srvaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    srvaddr.sin_port = htons(g_setting.net_port);

    g_setting.sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (bind(g_setting.sock, (struct sockaddr *)&srvaddr, sizeof(srvaddr)) < 0)
    {
        Log(err, "Server : can not bind local address port[%d]", g_setting.net_port);
        exit(0);
    }
    int enable = 1;
    if (setsockopt(g_setting.sock, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0)
        Log(err, "setsockopt(SO_REUSEADDR) failed");

    if (setsockopt(g_setting.sock, SOL_SOCKET, SO_RCVBUF, (char*)&g_setting.RCV_BUF, sizeof(g_setting.RCV_BUF)) < 0)
        Log(err, "setsockopt(SO_RCVBUF) failed");

    return 0;
}


void start_net_thread()
{
    if (0 == THREAD_USE) return;

    pthread_t p_thread;
    pthread_create(&p_thread, NULL, net_rcv_thread, (void *)NULL);
    pthread_detach(p_thread);
}

/*
thread that receives display data from led server
*/
void *net_rcv_thread(void *data)
{
    char *buf = new char[g_setting.RCV_BUF + 1024];
    int display_size = g_setting.W * g_setting.H * g_setting.C;
    uint8_t *display = new unsigned char[display_size];
    struct sockaddr_in  client_addr;
    int addr_len, recv_len, cur_size = 0, cur_display_size;
    int32_t key, seq, cnt, t;
    struct timeval start, end;
    float FPS;

    addr_len = sizeof(client_addr); 
    Log(info, "net_rcv_thread start");

    gettimeofday(&start, NULL);
    while(0 == g_setting.end){
        if((recv_len = recvfrom(g_setting.sock, buf, g_setting.RCV_BUF, 0, (struct sockaddr *)&client_addr, (socklen_t *)&addr_len)) < 0){ 
            Log(err, "recvfrom  failed:%s", strerror(errno));
            continue;
        }
        if(recv_len < 12) {
            Log(err, "recvfrom  invalid recv size:%d", recv_len);
            continue;
        }
        //htonl, ntohl always do 32bit int, 64bit int functions are htonll, ntohll.
        memcpy(&t, buf, 4);
        key = ntohl(t);

        memcpy(&t, buf + 4, 4);
        seq = ntohl(t);

        memcpy(&t, buf + 8, 4);
        cnt = ntohl(t);
        if(0 == seq){   //first packet
            gettimeofday(&start, NULL);
        }

        cur_display_size = recv_len - 12;
        Log(debug, "key:%d seq:%d tot:%d recv data:%d current_size:%d", key, seq, cnt, cur_display_size, cur_size + cur_display_size);
        if((cur_size + cur_display_size) > display_size){
            Log(err, "recv data overflows display size:%d  current_size:%d", display_size, cur_size + cur_display_size);
            cur_display_size = cur_size = 0;
        }

        memcpy(display + cur_size, buf + 12, cur_display_size);
        cur_size += cur_display_size;
        if(1 == key){   //Last packet
            if(cur_size != display_size){
                Log(err, "last frame : does not match display size:%d != current_size:%d", display_size, cur_size + cur_display_size);
                cur_display_size = cur_size = 0;
                continue;
            }
            if (0 == THREAD_USE){
                set_display(display); 
            }
            else{
                insert_queue(display);
            }
            gettimeofday(&end, NULL);
            FPS = calc_FPS(&start, &end);
            Log(info, "****Last Packet*** MAX FPS:%5.3f", FPS);
            cur_display_size = cur_size = 0;
             //insert buffer to display queue
        }
    }
    delete [] buf;
    delete [] display;
    close(g_setting.sock);
    Log(info, "net_rcv_thread end");
    return NULL;
}


float calc_FPS(const struct timeval *start, const struct timeval *end)
{
    long secs_used,micros_used;
    secs_used = end->tv_sec - start->tv_sec;
    micros_used=  end->tv_usec - start->tv_usec;
    float secs_elapsed = secs_used + micros_used * 1.0 / 1000000;
    return 1 / secs_elapsed;
}

/*
set display pixel with received np.array values.

<---------------- W * H * C ----------------> 
bgr bgr bgr bgr bgr bgr bgr bgr bgr bgr .....

*/
void set_display(const uint8_t *display)
{
    int frame =g_setting.W * g_setting.H;
    uint8_t r , g, b;
    int skip = 0;

    for (int y=0; y < g_setting.H; y++) {
        for (int x=0; x < g_setting.W ; x++) {
            skip = g_setting.W*y*3  + x*3;
            r = *(display + skip + 2);
            g = *(display + skip + 1);
            b = *(display + skip + x*3);
            g_canvas->SetPixel(x, y, r, g, b);
            if(x == 0){
                Log(debug, "R:%d G:%d B:%d", r, g, b);
            }
        }
    }
    g_canvas = g_matrix->SwapOnVSync(g_canvas);    
}

/*
if you use multi thread, display information will be inserted to queue and main thread will get it. 
*/
void insert_queue(const uint8_t *display)
{
    uint8_t *buf = (uint8_t *)malloc(g_setting.W * g_setting.H * g_setting.C);
    memcpy(buf, display, g_setting.W * g_setting.H * g_setting.C);
    pthread_mutex_lock(&g_setting.display_mutex);
    g_setting.display_queue.push_back(buf);
    pthread_mutex_unlock(&g_setting.display_mutex);
}

/*
You should free the return buf => free(buf)
*/
uint8_t *get_queue()
{
    uint8_t *buf = NULL;
    int size;
    pthread_mutex_lock(&g_setting.display_mutex);
    size = g_setting.display_queue.size();
    if(size){
        Log(info, "current display queue size:%d", size);
        buf = (uint8_t *)g_setting.display_queue.front();
        g_setting.display_queue.pop_front();    //remove from list
    }
    pthread_mutex_unlock(&g_setting.display_mutex);
    return buf;
}