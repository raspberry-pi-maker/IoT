import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
import time, os
import threading

images = ('count0.bmp', 'count1.bmp', 'count2.bmp')
count = 0
#frame 0 ~ 9: closed eye
#frame 10 ~ 59: open eye -->create eyeball
FPS = 10
SLEEP = 1.0 / FPS
img1 = cv2.imread(images[0])
img2 = cv2.imread(images[1])
img3 = cv2.imread(images[2])

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
    cv2.imshow('eye', img)
    cv2.waitKey(1)


def calc_led_pos(jetson_pos):
    LX_pos = int(L_Eye_Rgn[0] +  L_Eye_Rgn[2] * jetson_pos[0] / jetson_Rgn[0]) - int(leye_w / 2)
    LY_pos = int(L_Eye_Rgn[1] +  L_Eye_Rgn[3] * jetson_pos[1] / jetson_Rgn[1]) - int(leye_h / 2)
    RX_pos = int(R_Eye_Rgn[0] +  R_Eye_Rgn[2] * jetson_pos[0] / jetson_Rgn[0]) - int(reye_w / 2)
    RY_pos = int(R_Eye_Rgn[1] +  R_Eye_Rgn[3] * jetson_pos[1] / jetson_Rgn[1]) - int(reye_h / 2)
    return LX_pos, LY_pos, RX_pos, RY_pos


def set_eye(jetson_pos):
    lx, ly, rx, ry = calc_led_pos(jetson_pos)
    draw_eyeball(lx, ly, rx, ry)

L_Eye_Rgn = (90, 124, 122, 120) #x, y, W, H
R_Eye_Rgn = (330, 124, 118, 120) #x, y, W, H
jetson_Rgn = (640, 480) #W, H
g_jetson_pos = [320,240]   #initial position

'''
Thread function for drawing
'''
def draw_eye():
    while True:
        set_eye(g_jetson_pos)
        time.sleep(0.1)

def main():
    global g_jetson_pos
    t = threading.Thread(target=draw_eye, name='draw eye')
    t.daemon = True
    t.start()
    while True:
        try:
            num_str = input('enter eyeball center position  x, y :' ).split(',')
            if(len(num_str) != 2):
                print('invlid format. Enter like this  30, 50')
                continue
            pos = list(map(int, num_str))   #pos of center of face
            if pos[0] < 0 or pos[0] > jetson_Rgn[0]:
                print('invlid range. Enter X value 0 ~ 640')
                continue
            if pos[1] < 0 or pos[1] > jetson_Rgn[1]:
                print('invlid range. Enter Y value 0 ~ 480')
                continue

            g_jetson_pos = pos

        except KeyboardInterrupt:
            break    


if __name__ == '__main__':
    main()
