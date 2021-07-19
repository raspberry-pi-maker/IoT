#!/usr/bin/python3
import numpy as np
import cv2
import socket
import struct
import time
import argparse
from threading import Thread

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
from net_stream import NetStream

CHUNK_SIZE = 8192 + 32
CHUNK_SIZE = 52000

H = 128
W = 384
C = 3



parser = argparse.ArgumentParser(description='net run')
parser.add_argument('--port', type=int, default=4321, help='port number')
parser.add_argument('--cols', type=int, default=128, help='cols')
parser.add_argument('--rows', type=int, default=64, help='rows')
parser.add_argument('--chain_length', type=int, default=2, help='chain_length')
parser.add_argument('--parallel', type=int, default=3, help='parallel')
args = parser.parse_args()

VMapper = True


options = RGBMatrixOptions()
options.cols = args.cols
options.rows = args.rows
options.chain_length = args.chain_length
options.parallel = args.parallel
options.gpio_slowdown = 4
options.show_refresh_rate = 0
options.hardware_mapping = 'regular'  # I'm using Electrodragon HAT

#options.pixel_mapper_config = "Rotate:180"
options.pwm_bits = 7
options.pwm_dither_bits = 1
if VMapper == True:
    options.pixel_mapper_config = "V-mapper"


matrix = RGBMatrix(options=options)
double_buffer = matrix.CreateFrameCanvas()

player = NetStream(args.port).start()

while(True):
    try:
        if player.more_frame():
            final = player.read()
            im_pil = Image.fromarray(final)

            double_buffer.SetImage(im_pil)
            double_buffer = matrix.SwapOnVSync(double_buffer)
            
    except KeyboardInterrupt:
        break

player.statistics()
player.stop()