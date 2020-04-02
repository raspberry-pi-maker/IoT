import argparse
import time, os
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions



base_dir = '/usr/local/src'
parser = argparse.ArgumentParser(description='text effect run')
parser.add_argument('--text', type=str, default='안녕하세요. 반갑습니다. 좋은 날씨입니다.')
parser.add_argument('--font', type=str, default='SourceHanSansK-Bold')
parser.add_argument('--R', type=int, default=255, help='textcolor of R')
parser.add_argument('--G', type=int, default=255, help='textcolor of R')
parser.add_argument('--B', type=int, default=0, help='textcolor of R')
parser.add_argument('--image', type=str, default='%s/lotto/image/rainbow1.png'%(base_dir), help='background image')
args = parser.parse_args()

color_R = max(0, min(args.R, 255))
color_G = max(0, min(args.G, 255))
color_B = max(0, min(args.B, 255))

x_margin = 10
y_margin = -3
myfont = '%s/font/%s.otf'%(base_dir, args.font)

if os.path.exists(myfont) == False:
    print('Font[%s] Not found =>Use default[SourceHanSansK-Bold]'%(myfont))
    myfont = '%s/font/SourceHanSansK-Bold.otf'%(base_dir)

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

back_img = Image.open(args.image)
back_img = back_img.resize((img_width, 32))
mask = Image.new('RGBA', (img_width, 32),(0, 0, 0, 255))
draw = ImageDraw.Draw(mask)
fillcolor = (0,0,0,0)
draw.text((x_margin, y_margin), args.text, font=font, fill=fillcolor)
back_img.paste(mask, (0, 0), mask)
# back_img.save("/tmp/out.jpg")


xpos = 0
first = True
while True:
    xpos += 1
    if (xpos > (text_size + x_margin + 1)):
        break

    offscreen_canvas.SetImage(back_img, -xpos)
    offscreen_canvas.SetImage(back_img, -xpos + img_width)
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    if(first == True):
        first = False
        time.sleep(1)

    time.sleep(0.01)
time.sleep(1)
