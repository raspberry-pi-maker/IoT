import argparse
import time, os
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions


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

myfont = '/usr/local/src/font/%s.otf'%(args.font)

if os.path.exists(myfont) == False:
    print('Font[%s] Not found =>Use default[SourceHanSansK-Regular]'%(myfont))
    myfont = '/usr/local/src/font/nanumgothic.otf'

img_width = 64 * 4 * 2
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

image = Image.new('RGB', (img_width, 32),(0, 0, 0))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(myfont, 25)
draw.text((0,0), args.text, font=font, fill=(color_R,color_G,color_B,0))

xpos = 0
while True:
    xpos += 1
    if (xpos > img_width):
        xpos = 0

    offscreen_canvas.SetImage(image, -xpos)
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    time.sleep(0.01)






