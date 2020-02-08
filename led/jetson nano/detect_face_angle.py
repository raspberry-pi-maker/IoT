#!/usr/bin/python3
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#
# You should calculate the Width, Height / distance ratio. (This video may help you : https://www.youtube.com/watch?v=K9PUCmdXlQc)
# This value will vary depending on your camera type, resolution settings.
# In my case (Logitec HD 720P) 1280X720, 200mm(W)/ 220mm Distance -> 50 degree view angle (Even though camera specification says 60 degree)
#                               640X480, 150mm(W)/ 230mm Distance -> 43.6 degree view angle

import jetson.inference
import jetson.utils
from socket import *
import argparse
import sys, time
import numpy as np
import cv2
# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.3, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="/dev/video0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=640, help="desired width of camera stream (default is 640 pixels)")
parser.add_argument("--height", type=int, default=480, help="desired height of camera stream (default is 480 pixels)")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)


def calculate_size(w, h):
    return w * h

def find_big_face(detections):
    big_index = 0
    big_size =  0
    big_w = 0
    big_h = 0
    index = 0
    for detection in detections:
        size =  calculate_size(detection.Right - detection.Left, detection.Bottom - detection.Top)
        if(size > big_size):
            big_size = size
            big_w = detection.Right - detection.Left
            big_h = detection.Bottom - detection.Top
            big_index = index
        index += 1    
    return big_index, big_w, big_h

'''
find the center of the face
then calculate the angle of the center point
'''
def detect_face_angle(right, left, bottom, top):
    w_center = left + (right - left) / 2.0
    h_center = top + (bottom - top) / 2.0
    w_pixel = center[0] - w_center
    h_pixel = center[1] - h_center
    return w_pixel*pixel_degree, h_pixel*pixel_degree

#center of image
center = (int(opt.width / 2), int(opt.height / 2))
#1 pixel degree of my webcam (Logitec HD 720P 640X480)
pixel_degree = 43.6 / opt.width

# load the object detection network
net = jetson.inference.detectNet('facenet', threshold = opt.threshold)
# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
display = jetson.utils.glDisplay()

count = 0
img, width, height = camera.CaptureRGBA()
print("========== Capture Width:%d Height:%d ==========="%(width, height))
RPi_IP = '192.168.11.54'
RPi_PORT = 9090

RPi_sock = socket(AF_INET, SOCK_DGRAM)
# process frames until user exits
angle_threshold = [2.5, 1.5]
current_angle = [0.0, 0.0]
while True:
    try:
        s = time.time()
        move = False
        # capture the image
        img, width, height = camera.CaptureRGBA()

        # detect objects in the image (with overlay)
        detections = net.Detect(img, width, height, opt.overlay)

        # print the detections
        print("detected {:d} objects in image".format(len(detections)))
        if len(detections) == 0:
            continue

        fps = 1.0 / ( time.time() -s) 
        big_index, big_w, big_h = find_big_face(detections)
        w_angle, h_angle = detect_face_angle(detections[big_index].Right, detections[big_index].Left, detections[big_index].Bottom, detections[big_index].Top)
        if abs(w_angle - current_angle[0]) > angle_threshold[0]:
            move = True
            current_angle[0] = w_angle
        if abs(h_angle - current_angle[1]) > angle_threshold[1]:
            move = True
            current_angle[1] = h_angle

        display.RenderOnce(img, width, height)
        if move == True:
            print("FPS:%f , Big Face Angle H:%f degree V:%f degree"%(fps,w_angle,h_angle))
            packet = "%d,%d,%f,%f"%(big_w, big_h,current_angle[0], current_angle[1])
            RPi_sock.sendto(packet.encode(), (RPi_IP, RPi_PORT))

        # print out performance info
        # net.PrintProfilerTimes()
        count += 1
    except KeyboardInterrupt:
        break

