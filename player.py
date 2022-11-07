import sys
import math
import os

class Draw:
	def __init__(self):
		self.cmd = []

	def line(self, x1, y1, x2, y2, width, color):
		self.cmd.append("LINE {} {} {} {} {} {}".format(round(x1), round(y1), round(x2), round(y2), round(width), color))

	def ellipse(self, x, y, width, height, color):
		self.cmd.append("ELLIPSE {} {} {} {} {}".format(round(x), round(y), round(width), round(height), color))
	
	def circle(self, x, y, radius, color):
		self.cmd.append("CIRCLE {} {} {} {}".format(round(x), round(y), round(radius), color))
	
	def point(self, x, y, color):
		self.cmd.append("POINT {} {} {}".format(round(x), round(y), color))

	def flush(self):
		print(len(self.cmd))
		for d in self.cmd:
			print(d)
		self.cmd = []

class State:
	def __init__(self, x, y, hSpeed, vSpeed, fuel, rotate, power):
		self.x = x
		self.y = y
		self.hSpeed = hSpeed
		self.vSpeed = vSpeed
		self.fuel = fuel
		self.rotate = rotate
		self.power = power
		self.drawCmd = []
	
	def next(self, inputRotate, inputPower):
		nextRotate = self.rotate + min(15, max(-15, inputRotate - self.rotate))
		nextPower = self.power + (1 if inputPower > self.power else -1 if inputPower < self.power else 0)
		nextHSpeed = self.hSpeed + math.cos(math.radians(nextRotate - 90)) * nextPower
		nextVSpeed = self.vSpeed - math.sin(math.radians(nextRotate - 90)) * nextPower - 3.711
		nextX = self.x + nextHSpeed
		nextY = self.y + nextVSpeed
		nextFuel = self.fuel - nextPower
		return State(nextX, nextY, nextHSpeed, nextVSpeed, nextFuel, nextRotate, nextPower)
	
	def dict(self):
		return {
			"x": int(self.x),
			"y": int(self.y),
			"hSpeed": int(self.hSpeed),
			"vSpeed": int(self.vSpeed),
			"fuel": int(self.fuel),
			"rotate": int(self.rotate),
			"power": int(self.power),
			"drawCmd": self.drawCmd
		}


def crossLand(state):
	global land
	for i in range(len(land) - 1):
		if land[i][0] <= state.x <= land[i + 1][0]:
			# find the equation of the line
			# y = ax + b
			a = (land[i + 1][1] - land[i][1]) / (land[i + 1][0] - land[i][0])
			b = land[i][1] - a * land[i][0]
			return state.y <= a * state.x + b
	return False

def outOfBounds(state):
	return state.x < 0 or state.x > 6999 or state.y < 0 or state.y > 2999

def getOutput(hs, vs):
	angle_offset = -90 if hs > 0 else 90
	# print("rot:", 0 if hs == 0 else math.degrees(math.atan(vs / hs)) + angle_offset, file=sys.stderr, flush=True)
	return (
		int(0 if hs == 0 else math.degrees(math.atan(vs / hs)) + angle_offset),
		int(abs(math.sqrt(hs**2 + vs**2)))
	)

def truncOutput(r, s):
	return (
		90 if r > 90 else -90 if r < -90 else r,
		4 if s > 4 else 0 if s < 0 else s
	)

def norme(vec):
	return math.sqrt(vec[0]**2 + vec[1]**2)

def normalize(vec, scale=1):
	n = norme(vec)
	if n == 0:
		return vec
	return (vec[0] / n * scale, vec[1] / n * scale)

def calculeNextOutput(s):
	act_vec = (s.hSpeed, s.vSpeed+3.7)
	# print("vec actuel =", act_vec, file=sys.stderr, flush=True)

	# wish_vec = (landingPoint[0] - x, landingPoint[1] - y)
	wish_vec = (0, 0)
	wish_vec = normalize(wish_vec, 20)
	# print("vec voulu =", wish_vec, file=sys.stderr, flush=True)

	corr_vec = (wish_vec[0] - act_vec[0], wish_vec[1] - act_vec[1])
	# print("vec correctionel =", corr_vec, file=sys.stderr, flush=True)

	output = truncOutput(*getOutput(*corr_vec))
	if y < landingPoint[1] + 2000:
		output = (0, output[1])
		
	# print("Player output: {}".format(output), file=sys.stderr, flush=True)
	# output = (0, 4)
	return output

global n
n = 0
def simule(s):
	global n
	s = s.next(*calculeNextOutput(s))
	while not outOfBounds(s) and not crossLand(s):
		draw.line(s.x, s.y, s.x + s.hSpeed, s.y + s.vSpeed, 1, "#00FF00")
		output = calculeNextOutput(s)
		if n == 0:
			print(output, s.dict(), file=sys.stderr, flush=True)
		s = s.next(*output)
	n = 1

draw = Draw()

# retrieve lands points
surface_n = int(input())
land = []
for i in range(surface_n):
	land_x, land_y = [int(j) for j in input().split()]
	land.append((land_x, land_y))

# get landing point
landingPoint = (0, 0)
for i in range(surface_n - 1):
	if land[i][1] == land[i+1][1]:
		landingPoint = (int(land[i][0] + (land[i+1][0] - land[i][0]) / 2), land[i][1])

while True:
	x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]
	state = State(x, y, h_speed, v_speed, fuel, rotate, power)

	output = calculeNextOutput(state)
	print(*output, flush=True)
	print(*output, flush=True, file=sys.stderr)

	simule(state)

	draw.flush()