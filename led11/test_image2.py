#!/usr/bin/python3
import argparse
import numpy as np
import cv2
import time
from PIL import Image, ImageSequence
import netsender2 as netsender
import socket

canvas_w = 384
canvas_h = 512
parser = argparse.ArgumentParser(description='gif run')
parser.add_argument('--file', type=str, required=True, help='image file name')
args = parser.parse_args()

netsender.set_recv_pi([("192.168.11.11", 4321), ("192.168.11.12", 4321), ("192.168.11.13", 4321), ("192.168.11.14", 4321)])

img = cv2.imread(args.file, cv2.IMREAD_UNCHANGED)
img = cv2.resize(img, (canvas_w, canvas_h))
h, w, c = img.shape
if c == 4:
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

sleep_sec = 0.02
count = 0
total_sec = 0.0
while True:
    try:
        s = time.time()
        netsender.net_send(img)
        time.sleep(sleep_sec)
        count += 1
        total_sec += (time.time() - s)
    except KeyboardInterrupt:
        break
    except socket.timeout:
        continue

FPS = count / (total_sec)        
print('FPS:%4.2f'%(FPS))
