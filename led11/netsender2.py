#!/usr/bin/python3
import numpy as np
import cv2
import socket, struct,time

CHUNK_SIZE = 8192 * 6
#CHUNK_SIZE = 8192 * 5

g_recv_pi = []  # 포트 정보까지 포함함.[("192.168.11.100",4321), ("192.168.11.101",4321)]


'''
패킷을 받을 LED 플레이어 목록을 받는다.
스크린 사이즈 384(W) X 512(H)를 세로로 나눈다.
            384
       -------------
       |           |  128 (image)
       -------------
       |           |  128 (image)
       -------------     
       |           |  128 (image)
       -------------     
       |           |  128 (image)
       -------------     
'''
g_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
g_bufsize = g_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
print('Snd buf size:%d'%(g_bufsize))

def set_recv_pi(srvs):
    global g_recv_pi
    g_recv_pi = srvs.copy()
    print("network image receiver set to:" + str(g_recv_pi))


def net_send(img):
    h_img_0 = img[0:128, :]
    h_img_1 = img[128:256, :]
    h_img_2 = img[256:384, :]
    h_img_3 = img[384:512, :]
    total_0 = 0
    total_1 = 0
    total_2 = 0
    total_3 = 0
    data_0 = h_img_0.tobytes()
    data_1 = h_img_1.tobytes()
    data_2 = h_img_2.tobytes()
    data_3 = h_img_3.tobytes()
    
    chunks_0 = [data_0[i:i+CHUNK_SIZE] for i in range(0, len(data_0), CHUNK_SIZE)]
    chunks_1 = [data_1[i:i+CHUNK_SIZE] for i in range(0, len(data_1), CHUNK_SIZE)]
    chunks_2 = [data_2[i:i+CHUNK_SIZE] for i in range(0, len(data_2), CHUNK_SIZE)]
    chunks_3 = [data_3[i:i+CHUNK_SIZE] for i in range(0, len(data_3), CHUNK_SIZE)]
    chunk_len_0 = len(chunks_0)
    chunk_len_1 = len(chunks_1)
    chunk_len_2 = len(chunks_2)
    chunk_len_3 = len(chunks_3)
    
    maxcnt = max([chunk_len_0, chunk_len_1, chunk_len_2, chunk_len_3])
    s = time.time()

    for i in range(maxcnt):
        if(i == (chunk_len_0 - 1)): #last
            chunk_0 = struct.pack(">I", 1) + struct.pack(">I", i) + struct.pack(">I", chunk_len_0) + chunks_0[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        elif (i < (chunk_len_0 - 1)):
            chunk_0 = struct.pack(">I", 0) + struct.pack(">I", i) + struct.pack(">I", chunk_len_0) + chunks_0[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        else:     
            chunk_0 = None

        if(i == chunk_len_1 - 1): #last
            chunk_1 = struct.pack(">I", 1) + struct.pack(">I", i) + struct.pack(">I", chunk_len_1) + chunks_1[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        elif (i < chunk_len_1 - 1):
            chunk_1 = struct.pack(">I", 0) + struct.pack(">I", i) + struct.pack(">I", chunk_len_1) + chunks_1[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        else:     
            chunk_1 = None

        if(i == chunk_len_2 - 1): #last
            chunk_2 = struct.pack(">I", 1) + struct.pack(">I", i) + struct.pack(">I", chunk_len_2) + chunks_2[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        elif (i < chunk_len_2 - 1):
            chunk_2 = struct.pack(">I", 0) + struct.pack(">I", i) + struct.pack(">I", chunk_len_2) + chunks_2[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        else:     
            chunk_2 = None
            
        if(i == chunk_len_3 - 1): #last
            chunk_3 = struct.pack(">I", 1) + struct.pack(">I", i) + struct.pack(">I", chunk_len_3) + chunks_3[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        elif (i < chunk_len_3 - 1):
            chunk_3 = struct.pack(">I", 0) + struct.pack(">I", i) + struct.pack(">I", chunk_len_3) + chunks_3[i]    # len(data) + 12 bytes , ">I" : < means big-endian, I means 4 bytes integer
        else:     
            chunk_3 = None
            
            
        if chunk_0:
            g_sock.sendto(chunk_0, g_recv_pi[0])
            total_0 += len(chunk_0)
            #print('Srv[%s] Total snd:%d Key: , seq:%d total chunk:%d'%(g_recv_pi[0][0], total_0, i, chunk_len_0))
        if chunk_1:
            g_sock.sendto(chunk_1, g_recv_pi[1])
            total_1 += len(chunk_1)
        if chunk_2:
            g_sock.sendto(chunk_2, g_recv_pi[2])
            total_2 += len(chunk_2)
        if chunk_3:
            g_sock.sendto(chunk_3, g_recv_pi[3])
            total_3 += len(chunk_3)
        time.sleep(0.0001)    


    e = time.time()
    #print('Sending time:%f'%(e - s))