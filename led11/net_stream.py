# import the necessary packages
from threading import Thread
import sys, time
import socket
import numpy as np
import cv2
import struct

sleep_tm = 0.001

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
	from queue import Queue

# otherwise, import the Queue class for Python 2.7
else:
	from Queue import Queue



class NetStream:
    def __init__(self, port, CHUNK_SIZE = 52000, H = 128, W = 384, C = 3):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.port = port
        self.CHUNK_SIZE = CHUNK_SIZE
        self.stopped = False
        self.total = 0
        self.total_frame = 0
        self.total_succ_frame = 0
        self.total_err_frame = 0
        self.total_sec = 0.0
        self.buf = []
        self.packet_cnt = 0


        # initialize the queue used to store frames read from the udp
        self.Q = Queue(maxsize=16)
        self.H = H
        self.W = W
        self.C = C
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        bufsize = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        if self.CHUNK_SIZE < bufsize:
            self.CHUNK_SIZE = bufsize
        self.sock.settimeout(60)
        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        
    def reset(self):
        self.total = 0
        self.buf = []
        self.packet_cnt = 0

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely
        s = time.time()
        while self.stopped == False:
            # if the thread indicator variable is set, stop the
            # thread

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the UDP
                try:
                
                    data, addr = self.sock.recvfrom(self.CHUNK_SIZE)
                    self.total += len(data)
                    key = int.from_bytes(data[:4], byteorder="little")
                    seq = int.from_bytes(data[4:8], byteorder="little")
                    cnt = int.from_bytes(data[8:12], byteorder="little")
                    self.buf += data[12:]
                    self.packet_cnt += 1
                    if seq == 0:  #start
                        s = time.time()
                    if key == 1:  # last
                        self.total_frame += 1
                        img = np.asarray(self.buf, dtype=np.uint8)
                        img = img.reshape(self.H, self.W, self.C)
                        final = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        self.Q.put(final)
                        #print('put succ')
                        self.reset()
                        self.total_succ_frame += 1
                        self.total_sec += (time.time() - s)
                
                except ValueError:
                    self.reset()
                    self.total_err_frame += 1
                    print('Reshape Error')
                
                
            else:
                print('Error : Queue is full')
                time.sleep(sleep_tm)  # Rest for 10ms, we have a full queue

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def running(self):
        return self.more_frame() or not self.stopped

    def more_frame(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(sleep_tm)
            tries += 1

        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.sock.close()
        self.thread.join()
        
    def statistics(self):
        print('total frame :%d succ_frame:%d err_frame:%d'%(self.total_frame, self.total_succ_frame, self.total_err_frame)) 
        print('Avg packet processing time :%6.3f'%(self.total_sec / self.total_succ_frame)) 
