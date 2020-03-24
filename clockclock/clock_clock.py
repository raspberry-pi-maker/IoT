'''
2X2 문양 디자인
'''
import argparse
import numpy as np
import cv2
import time, sys
import math
from datetime import datetime
from PIL import Image, ImageDraw
import random


FPS = 30.0
SLEEP = 1.0 / FPS


tmargin = 1
lmargin = 13
rmargin = 12
margin = 1
bmargin = 1
r = 10

arm1_length = int(r * 1.0)
arm2_length = int(r * 0.8)
circle_thickness = 1
arm_thickness = 1
circle_color = (128,128,128)
arm_color = (96,128,255)
arm_color2 = (96,255,96)

Canvas_W = 192 #lmargin + rmargin + r * 2 * 8 + margin * 7
Canvas_H = 64  #tmargin + bmargin + r * 2 * 3 + margin * 2
step_angle = 1.8    

digit_basic = [[(45, -45),(45, -45),(45, -45)],  [(45, -45), ( 45, -45),( 45, -45)] ]
digit_1 = [ [(225, 225),(225, 225),(225, 225)],  [(180, 180),(  0, 180),(  0,   0)] ]
digit_2 = [ [( 90,  90),( 90, 180),(  0,  90)],  [(180, 270),(  0, 270),(270, 270)] ]
digit_3 = [ [( 90,  90),( 90,  90),( 90,  90)],  [(180, 270),(  0, 270),(  0, 270)] ]
digit_4 = [ [(180, 180),(  0,  90),(225, 225)],  [(180, 180),(  0, 180),(  0,   0)] ]
digit_5 = [ [( 90, 180),(  0,  90),( 90,  90)],  [(270, 270),(180, 270),(  0, 270)] ]
digit_6 = [ [( 90, 180),(  0, 180),(  0,  90)],  [(270, 270),(180, 270),(  0, 270)] ]
digit_7 = [ [( 90,  90),(225, 225),(225, 225)],  [(180, 270),(  0, 180),(  0,   0)] ]
digit_8 = [ [( 90, 180),(  0,  90),(  0,  90)],  [(180, 270),(  0, 270),(  0, 270)] ]
digit_9 = [ [( 90, 180),(  0,  90),( 90,  90)],  [(180, 270),(  0, 180),(  0, 270)] ]
digit_0 = [ [( 90, 180),(  0, 180),(  0,  90)],  [(180, 270),(  0, 180),(  0, 270)] ]
clock_digits = []
clock_digits.append(digit_0)
clock_digits.append(digit_1)
clock_digits.append(digit_2)
clock_digits.append(digit_3)
clock_digits.append(digit_4)
clock_digits.append(digit_5)
clock_digits.append(digit_6)
clock_digits.append(digit_7)
clock_digits.append(digit_8)
clock_digits.append(digit_9)

class Clock():
    def __init__(self, x, y, circle_color, circle_thick, arm_color, arm_thick, lmar):
        self.x = x
        self.y = y
        self.circle_color = circle_color
        self.circle_thickness = circle_thick
        self.arm_color = arm_color
        self.arm_thickness = arm_thick
        self.center = (lmar + r + (margin + 2*r) * x, tmargin + r + (margin + 2*r) * y)
        self.angle1 = 0.0
        self.angle2 =0.0
        self.step1 = step_angle
        self.step2 = step_angle
        self.arm1_dir = 1 #1:clockwise, 0:counter-clockwise
        self.arm2_dir = 1
        self.finish_angle1 = False
        self.finish_angle2 = False

    def draw_circle(self, img):
        cv2.circle(img, self.center, r, self.circle_color, self.circle_thickness)

    def draw_arms(self, img):
        # print('1 cur[%f] target[%f] 2 cur[%f] target[%f]'%(self.angle1, self.target_angle1, self.angle2, self.target_angle2))
        angle1 = np.radians(self.angle1)
        angle2 = np.radians(self.angle2)
        center = (lmargin + r + (margin + 2*r) * self.x, tmargin + r + (margin + 2*r) * self.y)
        pt = (self.center[0], self.center[1] - arm1_length) # 12 Hour direction

        qx = int(self.center[0] + math.cos(angle1) * (pt[0] - self.center[0]) - math.sin(angle1) * (pt[1] - self.center[1]))
        qy = int(self.center[1] + math.sin(angle1) * (pt[0] - self.center[0]) + math.cos(angle1) * (pt[1] - self.center[1]))
        cv2.line(img, self.center, (qx,qy), self.arm_color, self.arm_thickness)
        pt = (self.center[0], self.center[1] - arm2_length) # 12 Hour direction
        qx = int(self.center[0] + math.cos(angle1) * (pt[0] - self.center[0]) - math.sin(angle2) * (pt[1] - self.center[1]))
        qy = int(self.center[1] + math.sin(angle1) * (pt[0] - self.center[0]) + math.cos(angle2) * (pt[1] - self.center[1]))
        cv2.line(img, self.center, (qx,qy), self.arm_color, self.arm_thickness)

    def init_clock(self, img, step_cnt1, step_cnt2):
        self.set_angle(step_cnt1, step_cnt2)
        self.draw_circle(img)

    def set_angle(self, step_cnt1, step_cnt2):
        self.angle1 = step_cnt1 * self.step1
        self.angle2 = step_cnt2 * self.step2

    def get_angle(self):
        return self.angle1, self.angle2    

    def step_move(self, check, step1_move, step2_move):
        if check == True:
            if abs(self.angle1 - self.target_angle1) <= 0.001:    
                self.finish_angle1 = True
            else:
                if step1_move == True:
                    if self.arm1_dir == 1:
                        self.angle1 += self.step1
                        if self.angle1 >= 360.0:
                            self.angle1 -= 360.0
                    else:    
                        self.angle1 -= self.step1
                        if self.angle1 < 0.0:
                            self.angle1 += 360.0

            if abs(self.angle2 - self.target_angle2) <= 0.001:    
                self.finish_angle2 = True
            else:
                if step2_move == True:
                    if self.arm2_dir == 1:
                        self.angle2 += self.step2
                        if self.angle2 >= 360.0:
                            self.angle2 -= 360.0
                    else:    
                        self.angle2 -= self.step2
                        if self.angle2 < 0.0:
                            self.angle2 += 360.0
        else:
            if step1_move == True:
                if self.arm1_dir == 1:
                    self.angle1 += self.step1
                    if self.angle1 >= 360.0:
                        self.angle1 -= 360.0
                else:    
                    self.angle1 -= self.step1
                    if self.angle1 < 0.0:
                        self.angle1 += 360.0

            if step2_move == True:
                if self.arm2_dir == 1:
                    self.angle2 += self.step2
                    if self.angle2 >= 360.0:
                        self.angle2 -= 360.0
                else:    
                    self.angle2 -= self.step2
                    if self.angle2 < 0.0:
                        self.angle2 += 360.0
        return self.finish_angle1, self.finish_angle2

    '''
    타겟 angle값은 항상 1.8의 배수가 되도록 한다.
    '''
    def set_target_angle(self, step_cnt1, step_cnt2, arm1_dir = 1, arm2_dir = 1):
        step_cnt1 %= 200
        step_cnt2 %= 200
        self.arm1_dir = 1 #1:clockwise, 0:counter-clockwise
        self.arm2_dir = 1
        self.target_angle1 = step_cnt1 * self.step1
        self.target_angle2 = step_cnt2 * self.step2
        self.finish_angle1 = False
        self.finish_angle2 = False
        if arm1_dir == 1:
            angle = self.target_angle1 - self.angle1
        else:
            angle = self.angle1 - self.target_angle1
        if angle < 0.0:
            angle += 360.0
        step1 = int(angle / self.step1)

        if arm2_dir == 1:
            angle = self.target_angle2 - self.angle2
        else:
            angle = self.angle2 - self.target_angle2
        if angle < 0.0:
            angle += 360.0
        step2 = int(angle / self.step2)
        self.total_frames = max(step1, step2)
        self.current_frames = 0



class Clocks():
    def __init__(self, shift):
        self.myclocks = [[[0] for i in range(3)] for i in range(2)]
        self.shift = shift

    def initialize_clocks(self, img):
        for x in range(2):
            for y in range(3):
                clock = Clock(self.shift + x, y, circle_color, circle_thickness, arm_color, arm_thickness, lmargin)
                clock.arm1_dir = 1
                clock.arm2_dir = 1
                clock.init_clock(img, 25, 175)
                self.myclocks[x][y] = clock

    def set_digit(self, n):
        for x in range(2):
            for y in range(3):
                self.myclocks[x][y].set_target_angle(int(clock_digits[n][x][y][0] / step_angle), int(clock_digits[n][x][y][1] / step_angle))

    def step_move(self, img):
        rets = []
        for x in range(2):
            for y in range(3):
                ret = self.myclocks[x][y].step_move(True, True, True)
                self.myclocks[x][y].draw_arms(img)
                rets.append(ret[0])
                rets.append(ret[1])                

        if(all(rets) == True):
            return True , img
        else:
            return False , img   

    '''
    reset the clock arm target angle
    '''
    def reset_design_clock(self):
        for x in range(2):
            for y in range(3):
                c = self.myclocks[x][y]    
                c.set_target_angle(25, 175)

    def draw(self, img):
        for x in range(2):
            for y in range(3):
                c = self.myclocks[x][y]    
                c.draw_arms(img)
        return img        

def make_canvas(h, w, color):
    canvas = np.zeros([h,w,3], dtype=np.uint8)
    canvas.fill(color)
    return canvas

def initialize_clocks(img):
    H0_clocks.initialize_clocks(img)
    H1_clocks.initialize_clocks(img)
    M0_clocks.initialize_clocks(img)
    M1_clocks.initialize_clocks(img)

def restore_clocks(img):
    H0_clocks.reset_design_clock()
    H1_clocks.reset_design_clock()
    M0_clocks.reset_design_clock()
    M1_clocks.reset_design_clock()
    while True:
        rets = []
        s = time.time()
        tcanvas = img.copy()
        ret, tcanvas = H0_clocks.step_move(tcanvas)
        rets.append(ret)
        ret, tcanvas = H1_clocks.step_move(tcanvas)
        rets.append(ret)
        ret, tcanvas = M0_clocks.step_move(tcanvas)
        rets.append(ret)
        ret, tcanvas = M1_clocks.step_move(tcanvas)
        rets.append(ret)
        cv2.imshow("clock", tcanvas)
        cv2.waitKey(1)
        sleep_tm = SLEEP - (time.time() - s )
        time.sleep(max(0, sleep_tm))

        if(all(rets) == True):
            break


H0_clocks = Clocks(0)
H1_clocks = Clocks(2)
M0_clocks = Clocks(4)
M1_clocks = Clocks(6)

canvas = make_canvas(Canvas_H, Canvas_W, 0)  
initialize_clocks(canvas)
img = canvas.copy()
img = H0_clocks.draw(img)
img = H1_clocks.draw(img)
img = M0_clocks.draw(img)
img = M1_clocks.draw(img)
cv2.imshow("clock", img)
cv2.waitKey(100)

while True:
    now = datetime.now()
    H0_clocks.set_digit(int(now.hour / 10))
    H1_clocks.set_digit(now.hour % 10)
    M0_clocks.set_digit(int(now.minute / 10))
    M1_clocks.set_digit(now.minute % 10)
    while True:
        s = time.time()
        tcanvas = canvas.copy()
        rets = []
        try:
            ret, tcanvas = H0_clocks.step_move(tcanvas)
            rets.append(ret)
            ret, tcanvas = H1_clocks.step_move(tcanvas)
            rets.append(ret)
            ret, tcanvas = M0_clocks.step_move(tcanvas)
            rets.append(ret)
            ret, tcanvas = M1_clocks.step_move(tcanvas)
            rets.append(ret)
            cv2.imshow("clock", tcanvas)
            cv2.waitKey(1)
            sleep_tm = SLEEP - (time.time() - s )
            time.sleep(max(0, sleep_tm))

            if(all(rets) == True):
                break
        except KeyboardInterrupt:
            break
    tcanvas = canvas.copy()
    time.sleep(3)
    restore_clocks(tcanvas)
    print('restore end')

# ''' test 1 '''
# test_design(canvas)
# # img = clocks.restore_clock(canvas, 0, 100)
# cv2.waitKey(0)
# clocks.restore_design_clock(canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
