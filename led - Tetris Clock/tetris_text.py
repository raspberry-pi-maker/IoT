import argparse
import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import tetris_led as tetris


def getrevision():
    # Extract board revision from cpuinfo file
    myrevision = "0000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:8]=='Revision':
                length=len(line)
                myrevision = line[11:length-1]
        f.close()
    except:
        myrevision = "0000"

    version = None
    print('Raspberry Pi ReVersion:%s'%(myrevision))

    if myrevision == 'a03111' or myrevision == 'b03112' or myrevision == 'c03111':
        version = 4
    elif myrevision == 'a02082' or myrevision == 'a22082 ' or myrevision == 'a020d3 ':
        version = 3
    elif myrevision == 'a01041' or myrevision == 'a21041  ' or myrevision == 'a22042 ':
        version = 2
    elif myrevision == '900092' or myrevision == '900093  ' or myrevision == '9000C1 ':
        version = 0

    return myrevision, version

parser = argparse.ArgumentParser(description="RGB LED matrix Example")
parser.add_argument("--horizontal", type=int, default = 1, help="horizontal count")
parser.add_argument("--vertical", type=int, default = 1, help="vertical count")
args = parser.parse_args()

revisionm, version = getrevision()
# Configuration for the matrix
options = RGBMatrixOptions()
options.cols = 64
options.rows = 64
options.chain_length = args.horizontal * args.vertical
options.parallel = 1
options.brightness = 80

if(version == 4):
    options.gpio_slowdown =  4
elif(version == 3):
    options.gpio_slowdown =  1.0
else:    
    options.gpio_slowdown =  1

options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
options.pwm_dither_bits = 0

matrix = RGBMatrix(options = options)
double_buffer = matrix.CreateFrameCanvas()

canvas_w = args.horizontal * options.cols
canvas_h = args.vertical * options.rows
print('Canvas size W[%d] H[%d]'%(canvas_w, canvas_h))

tetris.set_scale(2)
tetris.set_bottom_shift(1)
tetris.make_canvas(canvas_h, canvas_w , 0)
tetris_str2 = tetris.TetrisString(1, tetris.CHAR_HEIGHT,  "ABCD")
tetris_str2.animate(matrix, double_buffer)

tetris.set_scale(1)
tetris_str = tetris.TetrisString(1, 0, "ABCDEFG")
tetris_str.animate(matrix, double_buffer)


time.sleep(10)