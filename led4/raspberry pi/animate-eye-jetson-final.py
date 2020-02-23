import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
import time, os
import threading
import socket
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration for the matrix
led_horizontal = 2
led_vertical = 2
cols = 64
rows=32

canvas_w = led_horizontal * cols
canvas_h = led_vertical * rows

options = RGBMatrixOptions()
options.cols = 64
options.rows = 32
options.chain_length = led_horizontal * led_vertical
options.parallel = 1
options.brightness = 80
options.pwm_bits = 11
options.gpio_slowdown = 1.0
options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # I use Electrodragon HAT
matrix = RGBMatrix(options = options)
double_buffer = matrix.CreateFrameCanvas()

images = ('count0.bmp', 'count1.bmp', 'count2.bmp', 'count3.bmp')
count = 0

img1 = cv2.imread(images[0])    #500 X 375 pixel size
img2 = cv2.imread(images[1])
img3 = cv2.imread(images[2])
img4 = cv2.imread(images[3])

left_eye = cv2.imread('left.png')
leye_h, leye_w, _ = left_eye.shape
right_eye = cv2.imread('right.png')
reye_h, reye_w, _ = right_eye.shape

def process_masking(base, mask, pos):
    h, w, c = mask.shape
    hb, wb, _ = base.shape
    x = pos[0]
    y = pos[1]
    masking_color = (103, 178, 199) #RGB
    #check mask position
    if(x > wb or y > hb):
        print(' invalid overlay position(%d,%d)'%(x, y))
        return None
    
    #remove alpha channel    
    if c == 4:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGRA2BGR) 
    
    #adjust mask
    if(x + w > wb):
        mask = mask[:, 0:wb - x]
        # print(' mask X size adjust[W:%d] -> [W:%d]'%(w, wb - x))
    if(y + h > hb):
        mask = mask[0:hb - y, :]
        # print(' mask Y size adjust[H:%d] -> [H:%d]'%(h, hb - y))

    h, w, c = mask.shape
    
    img = base.copy()
    bg = img[y:y+h, x:x+w]      #overlay area
    try:
        for i in range(0, h):
            for j in range(0, w):
                B = mask[i][j][0]
                G = mask[i][j][1]
                R = mask[i][j][2]
                # if (int(B) + int(G) + int(R)):
                if ((int(B) + int(G) + int(R)) and int(bg[i][j][0]) != masking_color[2]  and int(bg[i][j][1]) != masking_color[1]  and int(bg[i][j][2]) != masking_color[0] ):
                    bg[i][j][0] = B
                    bg[i][j][1] = G
                    bg[i][j][2] = R
        img[y:y+h, x:x+w] = bg
    except IndexError:  #index (i, j) is out of the screen resolution.  (화면 범위를 벗어남.)
        # print(' index Error')
        return None
    return img


def draw_eyeball(lx, ly, rx, ry):   #left eye POS, right eye POS (left, top position)
    img = img2.copy()
    img = process_masking(img, left_eye, (lx, ly))
    if img is None:
        return
    img = process_masking(img, right_eye, (rx, ry))
    if img is None:
        return
    led_display(img)
    # cv2.imshow('eye', img)
    # cv2.waitKey(1)


def calc_led_pos(jetson_pos):
    LX_pos = int(L_Eye_Rgn[0] +  L_Eye_Rgn[2] * jetson_pos[0] / jetson_Rgn[0]) - int(leye_w / 2)
    LY_pos = int(L_Eye_Rgn[1] +  L_Eye_Rgn[3] * jetson_pos[1] / jetson_Rgn[1]) - int(leye_h / 2)
    RX_pos = int(R_Eye_Rgn[0] +  R_Eye_Rgn[2] * jetson_pos[0] / jetson_Rgn[0]) - int(reye_w / 2)
    RY_pos = int(R_Eye_Rgn[1] +  R_Eye_Rgn[3] * jetson_pos[1] / jetson_Rgn[1]) - int(reye_h / 2)
    return LX_pos, LY_pos, RX_pos, RY_pos


def set_eye(jetson_pos):
    lx, ly, rx, ry = calc_led_pos(jetson_pos)
    draw_eyeball(lx, ly, rx, ry)

def draw_sleeping():
    for i in range(5):
            led_display(img1)
            # cv2.imshow('eye', img1)
            # cv2.waitKey(1)
            if(g_sleeping == False):
                break
            time.sleep(0.4)

    for i in range(5):
            led_display(img4)
            # cv2.imshow('eye', img4)
            # cv2.waitKey(1)
            if(g_sleeping == False):
                break
            time.sleep(0.2)

L_Eye_Rgn = (90, 124, 122, 120) #x, y, W, H
R_Eye_Rgn = (330, 124, 118, 120) #x, y, W, H
jetson_Rgn = (640, 480) #W, H
g_jetson_pos = [320,240]   #initial position
g_sleeping = False

'''
Thread function for drawing
'''
def draw_eye():
    while True:
        if(g_sleeping == False):
            set_eye(g_jetson_pos)
            time.sleep(0.1)
        else:
            draw_sleeping()

def led_display(img):
    global double_buffer
    im = cv2.resize(img, (canvas_w, canvas_h))
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    for x in range (led_vertical):
                i = im[rows * x: rows * (x + 1), 0:canvas_w]
                h, w, c = i.shape
                # print('split image H:%d W:%d'%(h, w))
                if ((led_vertical - x) % 2) == 0:    #-> flip
                    i = cv2.flip(i, 0) #vertical
                    i = cv2.flip(i, 1) #horizontal
                if(x == 0):
                    final = i
                else:
                    final = cv2.hconcat([final, i])   #stack horizontally
    im_pil = Image.fromarray(final)
    double_buffer.SetImage(im_pil)
    double_buffer = matrix.SwapOnVSync(double_buffer)


BindIP = '0.0.0.0'
RPI_PORT = 9090

def main():
    global g_jetson_pos, g_sleeping
    t = threading.Thread(target=draw_eye, name='draw eye')
    t.daemon = True
    t.start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BindIP, RPI_PORT))
    sock.settimeout(3)
    while True:
        try:
            buf, addr = sock.recvfrom(1024)
            g_sleeping = False
            buf = buf.decode('utf-8')
            data = buf.split(',')
            if(len(data) != 6):
                print('invalid data[%s]'%(buf))
                continue
            right = int(data[0])
            left = int(data[1])
            top = int(data[2])
            bottom = int(data[3])
            w_angle = float(data[4])
            h_angle = float(data[5])
            print('From Jetson face[right:%d,left:%d,top:%d,bottom:%d  w_angle:%f h_angle:%f]'%(right,left,top,bottom,w_angle,h_angle))
            g_jetson_pos = [int((right+left)/2), int((top+bottom)/2)]
        except socket.timeout:
            g_sleeping = True
            print('timeout')


        except KeyboardInterrupt:
            break    


if __name__ == '__main__':
    main()
