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


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", args.port))
bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
if CHUNK_SIZE < bufsize:
    CHUNK_SIZE = bufsize

print('Rcv buf size:%d' % (CHUNK_SIZE))
sock.settimeout(60)
total = 0
buf = []
packet_cnt = 0


def reset():
    global buf, total, packet_cnt
    total = 0
    buf = []
    packet_cnt = 0
    time.sleep(0.001)
'''
th = Thread(target=work, args=(1,))
th.daemon = True 
th.start()
'''
while(True):
    try:
        data, addr = sock.recvfrom(CHUNK_SIZE)
        total += len(data)
        key = int.from_bytes(data[:4], byteorder="big")
        seq = int.from_bytes(data[4:8], byteorder="big")
        cnt = int.from_bytes(data[8:12], byteorder="big")
        buf += data[12:]
        packet_cnt += 1
        #print('Total rcv:%d Key:%d, seq:%d total chunk:%d' %
        #      (total, key, seq, cnt))
        if key == 1:  # last
            # if(packet_cnt != cnt):
            #     print('Total rcv cnt:%d total chunk:%d'%(packet_cnt, cnt))
            #     reset()
            #     continue
            try:
                img = np.asarray(buf, dtype=np.uint8)
                img = img.reshape(H, W, C)
                final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = final.shape
                im_pil = Image.fromarray(final)
                #print('Reshape success')

                # double buffer를 사용하는 코드
                double_buffer.SetImage(im_pil)
                double_buffer = matrix.SwapOnVSync(double_buffer)
                # single buffer를 사용하는 코드
                #matrix.Clear()
                #matrix.SetImage(im_pil, 0)
                reset()
            except ValueError:
                reset()
                print('Reshape Error')

    except KeyboardInterrupt:
        break
    except socket.timeout:
        reset()
        continue

