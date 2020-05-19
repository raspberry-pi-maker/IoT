# TetrisClock that work on Raspberry Pi

TetrisClock is a WiFi clock made of falling tetris blocks. Oroginal TetrisClock runs on an ESP32 with an RGB LED Matrix.
----------------------------------

## TetrisClock <br />
![TetrisClock on the RGB LED Matrix by Brian Lough](./image/tetrisclock.gif) <br />

TetrisClock shown in the figure above works on the Arduino family of ESP32 MCUs. I wanted to implement this beautiful clock in Raspberry Pi, so I googled hard, but couldn't find any good examples. Eventually, I decided to analyze the code written in C language and implement it in Python and OpenCV.<br />
Creating a TetrisClock requires prior knowledge to drive the LED Matrix.
My blog https://iot-for-maker.blogspot.com/2020/05/led-make-tetrisclock.html explained what you need.


## Tetristext on the screen <br />
The following picture shows the Tetris text on the computer screen before implementing it in LED-Matrix.
![TetrisText](./image/tetris.gif) <br />


## TetrisClock on the RGB LED Matrix <br />
If you followed the content of the blog, you should see a Tetris watch that works like the following picture.

```console
python3 tetris_clock.py
```
</br>
I used a single 64x64 RGB LED Matrix. However, you can use a matrix of different sizes, and you can use multiple sheets. TetrisClock using ESP32 is optimized for a single 64X32 matrix, but my project, which works on Raspberry Pi, has the advantage that it can be applied to any size with minor modifications.

![TetrisText](./image/tetris_led.gif) <br />

The TetrisClock for Raspberry Pi relies heavily on Henner Zeller's excellent rpi-rgb-led-matrix library(https://github.com/hzeller/rpi-rgb-led-matrix). Also, my project would not have been possible without Brian Lough's example of implementing a great TetrisClock on ESP32( https://github.com/witnessmenow/WiFi-Tetris-Clock ).
