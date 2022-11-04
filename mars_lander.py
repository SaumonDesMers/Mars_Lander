from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import json
import sys
from simule import simule
import math
import random
import time

# check number of arguments
if len(sys.argv) != 3:
	print("Usage: python3 {} <input.json> <program>".format(sys.argv[0]))
	exit(1)

def error(msg):
	print("\033[91mError:\033[0m {}".format(msg))

playground_width = 7000
playground_height = 3000

def changeImage(slider):
	global image_on_canvas, tkimg
	img = pic[slider.get()]
	# resize the image to fit the canvas
	resizedImg = img.resize((canvas.winfo_width(), canvas.winfo_height()))
	tkimg = ImageTk.PhotoImage(resizedImg)
	canvas.itemconfig(image_on_canvas, image=tkimg)

# check input value
data: dict
def inputCheck():
	if data["surface_n"] < 2:
		error("not enough surface points: {}".format(data["surface_n"]))
		exit(1)
	if data["surface_n"] != len(data["land"]):
		error("surface_n do not match land points: {} != {}".format(data["surface_n"], len(data["land"])))
		exit(1)
	for i in range(data["surface_n"]):
		land = data["land"][i]
		if not (0 <= land["x"] <= playground_width and 0 <= land["y"] <= playground_height):
			error("land point {} out of bounds: {}".format(i, land))
			exit(1)
		if i > 0 and land["x"] <= data["land"][i - 1]["x"]:
			error("land x not increasing: {} <= {}".format(land["x"], data["land"][i - 1]["x"]))
			exit(1)
	if data["land"][0]["x"] != 0:
		error("first land x not 0: {}".format(data["land"][0]["x"]))
		exit(1)
	if data["land"][data["surface_n"] - 1]["x"] != playground_width - 1:
		error("last land x not {}: {}".format(playground_width - 1, data["land"][data["surface_n"] - 1]["x"]))
		exit(1)
	if not (0 <= data["start"]["x"] <= playground_width and 0 <= data["start"]["y"] <= playground_height):
		error("init point out of bounds: {}".format((data["start"]["x"], data["start"]["y"])))
		exit(1)
	if not (-500 <= data["start"]["hSpeed"] <= 500 and -500 <= data["start"]["vSpeed"] <= 500):
		error("init speed out of bounds: {}".format((data["start"]["hSpeed"], data["start"]["vSpeed"])))
		exit(1)
	if not (0 <= data["start"]["fuel"] <= 2000):
		error("init fuel out of bounds: {}".format(data["start"]["fuel"]))
		exit(1)
	if not (-90 <= data["start"]["rotate"] <= 90):
		error("init rotate out of bounds: {}".format(data["start"]["rotate"]))
		exit(1)
	if not (0 <= data["start"]["power"] <= 4):
		error("init power out of bounds: {}".format(data["start"]["power"]))
		exit(1)

try:
	data = json.load(open(sys.argv[1], "r"))
	inputCheck()
except Exception as e:
	error("could not parse input: {}".format(e))
	exit(1)

# create the root window
root = Tk()
root.title('Mars Lander')

def drawBg(draw):
	# draw background
	draw.rectangle((0, 0, cnv_width, cnv_height), fill="#000000")
	# draw surface
	for i in range(data["surface_n"] - 1):
		draw.line(
			(
				data["land"][i]["x"]*ration,
				playground_height*ration - data["land"][i]["y"]*ration,
				data["land"][i + 1]["x"]*ration,
				playground_height*ration - data["land"][i + 1]["y"]*ration
			),
			fill="#ffffff",
			width=2
		)

def drawLander(draw, game):
	size = 120 * ration
	x = game["x"] * ration
	y = (playground_height - game["y"]) * ration
	rotate = game["rotate"]
	landerRotate = math.radians(rotate - 90)
	# draw triangle for lander
	draw.polygon(
		(
			x + size*math.cos(landerRotate),
			y + size*math.sin(landerRotate),
			x + size/3 * math.cos(landerRotate + math.radians(90)),
			y + size/3 * math.sin(landerRotate + math.radians(90)),
			x + size/3 * math.cos(landerRotate + math.radians(-90)),
			y + size/3 * math.sin(landerRotate + math.radians(-90))
		),
		outline="#ffffff",
		width=2
	)
	# draw elipse for power
	random.seed(time.time())
	w, h = int(size/3), int(10*game["power"] * (1 + 0.3 * random.random()))
	elipseImg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
	drawElipse = ImageDraw.Draw(elipseImg)
	drawElipse.ellipse((0, 0, w-1, h-1), outline="#ffffff", width=2)
	elipseImg = elipseImg.rotate(-rotate, expand=True, fillcolor=(0, 0, 0, 0))
	draw.bitmap(
		(
			x + h/2 * math.cos(math.radians(rotate + 90)) - elipseImg.width/2,
			y + h/2 * math.sin(math.radians(rotate + 90)) - elipseImg.height/2
		),
		elipseImg,
		fill="#ffffff"
	)

# create the images
ration = 0.2
cnv_width = int(playground_width*ration)
cnv_height = int(playground_height*ration)
pic = []
game = simule(data, sys.argv[2])
picNb = len(game)
for i in range(picNb):
	image = Image.new('RGB', (cnv_width, cnv_height), (0, 0, 0))
	draw = ImageDraw.Draw(image)
	drawBg(draw)
	drawLander(draw, game[i])
	pic.append(image)

# create slider for video
slider = Scale(root, from_=0, to=picNb-1, orient=HORIZONTAL, command=lambda e: changeImage(slider))
slider.pack(fill=X, side=BOTTOM)

# update slider with arrow keys
def key(event):
	if event.keysym == 'Left':
		slider.set(slider.get() - 1)
	elif event.keysym == 'Right':
		slider.set(slider.get() + 1)
	elif event.keysym == 'Escape':
		root.destroy()
root.bind_all('<Key>', key)

# update slider with mouse wheel
root.bind_all('<MouseWheel>', lambda e: slider.set(slider.get() - int(e.delta/120)))

# update image on resize
root.bind('<Configure>', lambda e: changeImage(slider))

# create canvas
canvas = Canvas(root, bg='black')
canvas.pack(expand=True, fill=BOTH)

# create the image on the canvas
image_on_canvas = canvas.create_image(0, 0, anchor=NW, image=None)

# update window size to fit canvas
root.update()
root.geometry('{}x{}'.format(cnv_width, cnv_height))

# update the image on the canvas after mainloop
root.after(10, lambda: [slider.set(0), changeImage(slider)])

root.mainloop()