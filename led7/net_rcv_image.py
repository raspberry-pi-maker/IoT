import argparse, sys
import numpy as np
import cv2
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import socket, struct,time
 
parser = argparse.ArgumentParser(description="RGB LED matrix Example")
parser.add_argument("--chain", type=int, default = 1, help="chain count") 
args = parser.parse_args() 
 
 
CHUNK_SIZE = 52000
SERVER = ("0.0.0.0",4321)
'''
Display size information
'''
H = 64
W = 128
C = 3

'''
I will flip half of the image. Because I'm using one HUB75 chain.
See https://iot-for-maker.blogspot.com/2020/01/led-5-lets-make-large-led-display-part_21.html
'''
if args.chain == 1:
    y_end = int(H / 2)
elif args.chain == 2:
    y_end = int(H)
else:
    print('Invlaid chain number:%d must be(1 or 2)'%(args.chain))
    sys.exit()    
x_end = W

# Configuration for the matrix
options = RGBMatrixOptions()
options.cols = 64
options.rows = 32
options.chain_length = int(4 / args.chain)
options.parallel = args.chain
options.gpio_slowdown = 3.5
options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # I'm using Electrodragon HAT
matrix = RGBMatrix(options = options)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER)
bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) 
print('Rcv buf size:%d'%(bufsize))

if CHUNK_SIZE < bufsize:
    CHUNK_SIZE = bufsize

sock.settimeout(20)
total = 0
buf = []
packet_cnt = 0

def reset():
    global buf, total, packet_cnt
    total = 0
    buf = []
    packet_cnt = 0

while(True):
    try:
        data, addr = sock.recvfrom(CHUNK_SIZE)
        total += len(data)
        key = int.from_bytes(data[:4],byteorder="little")
        seq = int.from_bytes(data[4:8],byteorder="little")
        cnt = int.from_bytes(data[8:12],byteorder="little")
        buf += data[12:]
        packet_cnt += 1
        #print('Total rcv:%d Key:%d, seq:%d total chunk:%d'%(total, key, seq, cnt))
        if key == 1:    #last
            if(packet_cnt != cnt):
                print('Total rcv cnt:%d total chunk:%d'%(packet_cnt, cnt))
                reset()
                continue
            img = np.asarray(buf, dtype=np.uint8)
            img = img.reshape(H,W,C)
            
            if args.chain == 1:
                '''
                split the image top, bottom
                '''
                top_img = img[0: y_end, 0:x_end]
                bottom_img = img[y_end: y_end * 2, 0:x_end]

                '''
                flip the top image
                '''
                top_img = cv2.flip(top_img, 0) #vertical
                top_img = cv2.flip(top_img, 1) #horizontal    
                img = np.concatenate((top_img, bottom_img), axis=1)   #stack horizontally 
                
            final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)     #PIL use RGB Format
            #print('final image size:H%d W:%d'% (final.shape[0], final.shape[1]))

            im_pil = Image.fromarray(final)
            matrix.Clear()
            matrix.SetImage(im_pil, 0)
            reset()

    except KeyboardInterrupt:
        break
    except socket.timeout:
        reset()
        continue    


