import math
from PIL import Image, ImageDraw

size = 120
power = 4
rotate = 45
w, h = int(size/3), int(10*power)
elipseImg = Image.new("RGBA", (w, h), (0, 0, 0))
drawElipse = ImageDraw.Draw(elipseImg)
drawElipse.ellipse((0, 0, w-1, h-1), outline="#ffffff")
# elipseImg = elipseImg.rotate(math.radians(rotate), expand=True, fillcolor=(255, 0, 0))
elipseImg.show()