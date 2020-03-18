import argparse
import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time

parser = argparse.ArgumentParser(description="RGB LED matrix Example")
parser.add_argument("--video", type=str, required = True, help="video file name")
parser.add_argument("--horizontal", type=int, default = 1, help="horizontal count")
parser.add_argument("--vertical", type=int, default = 1, help="vertical count")
args = parser.parse_args()

FPS = 30.0
SLEEP = 1.0 / FPS
# Configuration for the matrix
options = RGBMatrixOptions()
options.cols = 64
options.rows = 32
options.chain_length = args.horizontal * args.vertical
options.parallel = 1
options.brightness = 80
options.pwm_bits = 11
options.gpio_slowdown = 1.0
options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.pwm_dither_bits = 0

matrix = RGBMatrix(options = options)

canvas_w = args.horizontal * options.cols
canvas_h = args.vertical * options.rows

print('Matrix H:%d W:%d'%(matrix.height, matrix.width))
print('Image size H:%d W:%d'%(canvas_h, canvas_w))

cap = cv2.VideoCapture(args.video)

double_buffer = matrix.CreateFrameCanvas()

while cap.isOpened():
    imgs = []
    start = time.time()
    for i in range(2):
        ret, im = cap.read()
        if(ret == False):
            break
        im = cv2.resize(im, (canvas_w, canvas_h))
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        imgs.append(im)

    if(ret == False):
        break

    im_pils = []
    for img in imgs:
        for x in range (args.vertical):
            i = img[options.rows * x: options.rows * (x + 1), 0:canvas_w]
            h, w, c = i.shape
            # print('split image H:%d W:%d'%(h, w))
            if ((args.vertical - x) % 2) == 0:    #-> flip
                i = cv2.flip(i, 0) #vertical
                i = cv2.flip(i, 1) #horizontal
            if(x == 0):
                final = i
            else:
                final = cv2.hconcat([final, i])   #stack horizontally

        h, w, c = final.shape
        # print('final image H:%d W:%d'%(h, w))
        im_pil = Image.fromarray(final)
        im_pils.append(im_pil)
        # matrix.Clear()
        #matrix.SetImage(im_pil, 0)

    double_buffer.SetImage(im_pils[0])
    double_buffer.SetImage(im_pils[1], canvas_w)
    double_buffer = matrix.SwapOnVSync(double_buffer)

    elapsed = time.time() - start
    #print('elapsed:%f'%(elapsed))
    time.sleep(max([0, SLEEP - elapsed]))
