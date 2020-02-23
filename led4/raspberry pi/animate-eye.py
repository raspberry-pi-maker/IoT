import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
import time, os

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
right_eye = cv2.imread('right.png')

gif_frames = []

def save_gif(frames, gifname, speed):   #speed 100
    frames[0].save(gifname, format='GIF', append_images=frames[1:], save_all=True, duration=speed, loop=0)

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
        print(' mask X size adjust[W:%d] -> [W:%d]'%(w, wb - x))
    if(y + h > hb):
        mask = mask[0:hb - y, :]
        print(' mask Y size adjust[H:%d] -> [H:%d]'%(h, hb - y))

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
        print(' index Error')
        return None
    return img


def draw_eyeball(lx, ly, rx, ry):   #left eye POS, right eye POS
    img = img2.copy()
    img = process_masking(img, left_eye, (lx, ly))
    if img is None:
        return
    img = process_masking(img, right_eye, (rx, ry))
    if img is None:
        return
    cv2.imshow('eye', img)
    cv2.waitKey(1)
    if(count == 0):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        gif_frames.append(im_pil)

def play_eye(img, tm):
    start = time.time()
    cv2.imshow('eye', img)
    cv2.waitKey(1)
    if(count == 0):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        gif_frames.append(im_pil)
    end = time.time()
    time.sleep(max(0, (tm - (end - start))))

def play_open_eye():
    reye_center = (350, 160)
    reye_left = (250, 160)
    reye_right = (450, 160)
    leye_center = (115, 150)
    leye_left = (20, 150)
    leye_right = (214, 150)
    dx_cnt = 10
    drx = (reye_center[0] - reye_left[0]) / dx_cnt
    dlx = (leye_center[0] - leye_left[0]) / dx_cnt
    for i in range(dx_cnt):
        start = time.time()
        print('(%d, %d), (%d,%d)'%(leye_center[0] + dlx * i, leye_center[1], reye_center[0] + drx * i, reye_center[1]))
        draw_eyeball(int(leye_center[0] + dlx * i), leye_center[1], int(reye_center[0] + drx * i) , reye_center[1])
        end = time.time()
        time.sleep(max(0, SLEEP - (end - start)))

    #right->left
    for i in range(dx_cnt * 2):
        start = time.time()
        draw_eyeball(int(leye_right[0] - dlx * i), leye_right[1], int(reye_right[0] - drx * i), reye_right[1])
        end = time.time()
        time.sleep(max(0, SLEEP - (end - start)))

    #left -> center
    for i in range(dx_cnt ):
        start = time.time()
        draw_eyeball(int(leye_left[0] + dlx * i), leye_left[1], int(reye_left[0] + drx * i), reye_left[1])
        end = time.time()
        time.sleep(max(0, SLEEP - (end - start)))
    #center stop    
    for i in range(dx_cnt ):
        start = time.time()
        draw_eyeball(int(leye_center[0] ), leye_center[1], int(reye_center[0] ) , reye_center[1])
        end = time.time()
        time.sleep(max(0, SLEEP - (end - start)))
    #close eye

    #half eye
    play_eye(img3, SLEEP)
    # play_eye(img1, SLEEP * 2)

count = 0
while True:
    try:
        print('play closed eye')
        play_eye(img1, SLEEP * FPS)
        print('play  open eye')
        play_open_eye()
        if(count == 0):
            save_gif(gif_frames, "./eye_test.gif", 100)
        count += 1
    except KeyboardInterrupt:
        break    

