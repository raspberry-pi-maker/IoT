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

# Configuration for the matrix
options = RGBMatrixOptions()
options.cols = 64 * 2
options.rows = 32 * 2
options.chain_length = args.horizontal 
options.parallel = args.vertical
options.brightness = 70
options.pwm_bits = 11
options.gpio_slowdown = 3.5
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
ret, im = cap.read()
h, w, _ = im.shape
print('Video frame size H:%d W:%d'%(h, w))
double_buffer = matrix.CreateFrameCanvas()

'''
while cap.isOpened():
    start = time.time()
    ret, im = cap.read()
    if(ret == False):
        break
    im = cv2.resize(im, (canvas_w, canvas_h))
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(im)

    double_buffer.SetImage(im_pil)
    double_buffer.SetImage(im_pil, canvas_w)
    double_buffer = matrix.SwapOnVSync(double_buffer)

    elapsed = time.time() - start
    #print('elapsed:%f'%(elapsed))
    time.sleep(max([0, (0.066 - elapsed)/2] ))

'''
while cap.isOpened():
    start = time.time()
    ret, im = cap.read()
    if(ret == False):
        break
    im = cv2.resize(im, (canvas_w, canvas_h))
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(im)
    double_buffer.SetImage(im_pil)
    double_buffer = matrix.SwapOnVSync(double_buffer)
    elapsed = time.time() - start
    #print('elapsed:%f'%(elapsed))
    time.sleep(max([0, 0.066 - elapsed]))
    
