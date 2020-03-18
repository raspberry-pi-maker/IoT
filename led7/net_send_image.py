'''
This code may run on any PC or Raspberry
'''

import numpy as np
import cv2
import socket, struct,time

CHUNK_SIZE = 8192 * 6

'''
Modify this information for your environment
'''
RPI = [ ("192.168.11.84", 4321), ("192.168.11.91", 4321)]

Image_W = 64* 4
Image_H = 32* 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) 

print('Snd buf size:%d'%(bufsize))

img = cv2.imread('wide_image.jpg')
H,W,C = img.shape
img = cv2.resize(img, (Image_W, Image_H))

splt_img = np.hsplit(img, 2)
print('split image size:H%d W:%d'% (splt_img[0].shape[0], splt_img[0].shape[1]))
data = []
for j in splt_img:
    data.append(j.tobytes())

chunks = []
snd_chunks = []
chunk_len = []
s = time.time()

'''
The chunk and struct packing work is done in advance to finish the transfer quickly
'''
for x in range(0,2):
    print(x)
    chunks.append([data[x][i:i+CHUNK_SIZE] for i in range(0, len(data[x]), CHUNK_SIZE)])
    chunk_len.append(len(chunks[x]))

    for i, chunk in enumerate(chunks[x]):
        if(i == chunk_len[x] - 1): #last
            chunk = struct.pack("<I", 1) + struct.pack("<I", i) + struct.pack("<I", chunk_len[x]) + chunk    # len(data) + 12 bytes , "<I" : < means little-endian, I means 4 bytes integer
        else:    
            chunk = struct.pack("<I", 0) + struct.pack("<I", i) + struct.pack("<I", chunk_len[x]) + chunk    # len(data) + 12 bytes , "<I" : < means little-endian, I means 4 bytes integer
        snd_chunks.append(chunk)

total = 0
'''
To end the transfer at the same time , Send alternately.
'''
for x in range(chunk_len[0]):
    sock.sendto(snd_chunks[x], RPI[0])
    total += len(snd_chunks[x])
    sock.sendto(snd_chunks[x + chunk_len[0]], RPI[1])
    total += len(snd_chunks[x + chunk_len[0]])
    print('Total sent:%d'%(total))

e = time.time()
print('time:%f'% (e - s))