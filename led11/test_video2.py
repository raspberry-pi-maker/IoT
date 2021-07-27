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
parser.add_argument('--file', type=str, default='./souffle.mp4', help='video file name')
args = parser.parse_args()

netsender.set_recv_pi([("192.168.11.11", 4321), ("192.168.11.12", 4321), ("192.168.11.13", 4321), ("192.168.11.14", 4321)])

cap = cv2.VideoCapture(args.file)
while cap.isOpened():
    try:
        s = time.time()
        ret, img = cap.read()
        if ret == False:
            break
        img = cv2.resize(img, (canvas_w, canvas_h))
        netsender.net_send(img)
        #0.06에러 0.07 성공 
        time.sleep(0.005)
        print('FPS:%4.2f'%(1 / (time.time() - s)))
    except KeyboardInterrupt:
        break
    except socket.timeout:
        continue


