import argparse
import time, os
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions


parser = argparse.ArgumentParser(description='text effect run')
parser.add_argument('--text', type=str, default='안녕하세요. 반갑습니다.')
parser.add_argument('--font', type=str, default='SourceHanSansK-Bold')
parser.add_argument('--R', type=int, default=255, help='linecolor of R')
parser.add_argument('--G', type=int, default=255, help='linecolor of R')
parser.add_argument('--B', type=int, default=0, help='linecolor of R')
parser.add_argument('--fR', type=int, default=0, help='fillcolor of R')
parser.add_argument('--fG', type=int, default=0, help='fillcolor of G')
parser.add_argument('--fB', type=int, default=0, help='fillcolor of B')
parser.add_argument('--t', type=int, default=1, help='thickness')
args = parser.parse_args()

color_R = max(0, min(args.R, 255))
color_G = max(0, min(args.G, 255))
color_B = max(0, min(args.B, 255))

f_R = max(0, min(args.fR, 255))
f_G = max(0, min(args.fG, 255))
f_B = max(0, min(args.fB, 255))
x_margin = 3
y_margin = -3
myfont = '/usr/local/src/font/%s.otf'%(args.font)

if os.path.exists(myfont) == False:
    print('Font[%s] Not found =>Use default[SourceHanSansK-Bold]'%(myfont))
    myfont = '/usr/local/src/font/SourceHanSansK-Bold.otf'

options = RGBMatrixOptions()
options.cols = 64
options.rows = 32
options.chain_length =  4
options.parallel = 1
options.gpio_slowdown =  1
options.show_refresh_rate = 1
options.hardware_mapping = 'regular'  # I'm using Electrodragon HAT
matrix = RGBMatrix(options = options)
offscreen_canvas = matrix.CreateFrameCanvas()

font = ImageFont.truetype(myfont, 25)
text_size = font.getsize(args.text)[0]
img_width = text_size * 2
image = Image.new('RGB', (img_width, 32),(0, 0, 0))
draw = ImageDraw.Draw(image)



draw.text((x_margin - args.t, y_margin) ,args.text, font=font, fill=(color_R, color_G,color_B))
draw.text((x_margin + args.t, y_margin) ,args.text, font=font, fill=(color_R, color_G,color_B))
draw.text((x_margin, y_margin + args.t) ,args.text, font=font, fill=(color_R, color_G,color_B))
draw.text((x_margin, y_margin - args.t) ,args.text, font=font, fill=(color_R, color_G,color_B))
draw.text((x_margin, y_margin) ,args.text, font=font, fill=(f_R, f_G,f_B))

xpos = 0
first = True
while True:
    xpos += 1
    if (xpos > img_width):
        break

    offscreen_canvas.SetImage(image, -xpos)
    offscreen_canvas.SetImage(image, -xpos + img_width)
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    if(first == True):
        first = False
        time.sleep(1)    
    time.sleep(0.01)
time.sleep(1)





