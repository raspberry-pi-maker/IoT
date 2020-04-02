import argparse
import time, os
from PIL import Image, ImageDraw 
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


parser = argparse.ArgumentParser(description='face match run')
parser.add_argument('--text', type=str, default='안녕하세요. 반갑습니다.')
parser.add_argument('--font', type=str, default='SourceHanSansK-Regular')
parser.add_argument('--R', type=int, default=255)
parser.add_argument('--G', type=int, default=255)
parser.add_argument('--B', type=int, default=0)
args = parser.parse_args()

color_R = max(0, min(args.R, 255))
color_G = max(0, min(args.G, 255))
color_B = max(0, min(args.B, 255))

myfont = '/usr/local/src/font/%s.bdf'%(args.font)

if os.path.exists(myfont) == False:
    print('Font[%s] Not found =>Use default[SourceHanSansK-Regular]'%(myfont))
    myfont = '/usr/local/src/font/SourceHanSansK-Regular.bdf'

options = RGBMatrixOptions()
options.cols = 64
options.rows = 32
options.chain_length =  4
options.parallel = 1
options.gpio_slowdown =  2
options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # I'm using Electrodragon HAT
matrix = RGBMatrix(options = options)

offscreen_canvas = matrix.CreateFrameCanvas()
font = graphics.Font()
font.LoadFont(myfont)
textColor = graphics.Color(color_R, color_G, color_B)
pos = offscreen_canvas.width
my_text = args.text

while True:
    offscreen_canvas.Clear()
    len = graphics.DrawText(offscreen_canvas, font, pos, 25, textColor, my_text)
    pos -= 1
    if (pos + len < 0):
        pos = offscreen_canvas.width

    time.sleep(0.05)
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)




