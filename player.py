import sys
import math
import os

class Draw:
	def __init__(self):
		self.cmd = []

	def line(self, x1, y1, x2, y2, width, color):
		self.cmd.append("LINE {} {} {} {} {} {}".format(int(x1), int(y1), int(x2), int(y2), int(width), color))

	def ellipse(self, x, y, width, height, color):
		self.cmd.append("ELLIPSE {} {} {} {} {}".format(int(x), int(y), int(width), int(height), color))
	
	def circle(self, x, y, radius, color):
		self.cmd.append("CIRCLE {} {} {} {}".format(int(x), int(y), int(radius), color))
	
	def point(self, x, y, width, color):
		self.cmd.append("POINT {} {} {} {}".format(int(x), int(y), int(width), color))

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
		nextPower = min(nextPower, self.fuel)
		nextHSpeed = self.hSpeed + math.cos(math.radians(nextRotate)) * nextPower
		nextVSpeed = self.vSpeed + math.sin(math.radians(nextRotate)) * nextPower - 3.711
		nextX = self.x + nextHSpeed
		nextY = self.y + nextVSpeed
		nextFuel = self.fuel - nextPower
		return State(nextX, nextY, nextHSpeed, nextVSpeed, nextFuel, nextRotate, nextPower)

	def nexts(self, inputList):
		stateList = []
		for input in inputList:
			state = self.next(input[0], input[1])
			stateList.append(state)
		return stateList

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

	def __str__(self):
		return "State(x={}, y={}, hSpeed={}, vSpeed={}, fuel={}, rotate={}, power={})".format(
			int(self.x), int(self.y), int(self.hSpeed), int(self.vSpeed), int(self.fuel), int(self.rotate), int(self.power)
		)


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
	power = int(math.sqrt(hs**2 + vs**2))
	if vs < 0:
		power = 3
	return (
		int(math.degrees(math.atan2(abs(vs), hs))),
		power
	)

def truncOutput(r, s):
	return (
		180 if r > 180 else 0 if r < 0 else r,
		4 if s > 4 else 0 if s < 0 else s
	)

def norme(vec):
	return math.sqrt(vec[0]**2 + vec[1]**2)

def normalize(vec, scale=1):
	n = norme(vec)
	if n == 0:
		return vec
	return (vec[0] / n * scale, vec[1] / n * scale)

def landingPoint(s):
	global landingSurface
	offset = 100
	lp = (0, 0)
	if s.x < landingSurface["x1"] + offset:
		lp = (landingSurface["x1"] + offset, landingSurface["y"])
	elif s.x > landingSurface["x2"] - offset:
		lp = (landingSurface["x2"] - offset, landingSurface["y"])
	else:
		lp = (s.x, landingSurface["y"])
	return lp

def calculeNextOutput(s, debug=False):

	ns_idle = s.next(s.rotate, s.power)

	act_vec = (s.hSpeed, s.vSpeed)
	# print("vec actuel =", act_vec, file=sys.stderr, flush=True)

	# dest_point = (3000, 1500)
	dest_point = landingPoint(s)

	wish_vec = (dest_point[0] - ns_idle.x, dest_point[1] - ns_idle.y)
	# wish_vec = (0, 10)
	wish_vec = normalize(wish_vec, 100)
	# print("vec voulu =", wish_vec, file=sys.stderr, flush=True)

	corr_vec = (wish_vec[0] - act_vec[0], wish_vec[1] - act_vec[1])
	# print("vec correctionel =", corr_vec, file=sys.stderr, flush=True)

	output = getOutput(*corr_vec)
	tOutput = truncOutput(*output)

	if s.y < dest_point[1] + 500:
		tOutput = (90, 4)
		
	# tOutput = (0, 4)

	ns = s.next(*tOutput)
	if debug:
		draw.line(ns.x, ns.y, ns.x + act_vec[0], ns.y + act_vec[1], 2, "#00ff00")
		draw.line(ns.x, ns.y, ns.x + wish_vec[0], ns.y + wish_vec[1], 2, "#0000ff")
		draw.line(ns.x, ns.y, ns.x + corr_vec[0], ns.y + corr_vec[1], 2, "#ff0000")
		draw.point(dest_point[0], dest_point[1], 10, "#ffff00")

		_x = ns.x + math.cos(math.radians(output[0])) * output[1]
		_y = ns.y + math.sin(math.radians(output[0])) * output[1]
		draw.line(ns.x, ns.y, _x, _y, 2, "#00ffff")
	
	return tOutput

def simule(s):
	global step
	s = s.next(*calculeNextOutput(s))
	while not outOfBounds(s) and not crossLand(s):
		draw.line(s.x, s.y, s.x + s.hSpeed, s.y + s.vSpeed, 1, "#555555")
		draw.point(s.x, s.y, 5, "#777777")
		output = calculeNextOutput(s)
		# if step == 0:
		# 	print(s, "->", output, file=sys.stderr, flush=True)
		
		s = s.next(*output)

draw = Draw()

# retrieve lands points
surface_n = int(input())
land = []
for i in range(surface_n):
	land_x, land_y = [int(j) for j in input().split()]
	land.append((land_x, land_y))

# get landing point
landingSurface = (0, 0, 0)
for i in range(surface_n - 1):
	if land[i][1] == land[i+1][1]:
		landingSurface = {
			"x1": land[i][0], 
			"x2": land[i+1][0],
			"y": land[i][1]
		}

step = 0
while True:
	x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]
	state = State(x, y, h_speed, v_speed, fuel, rotate, power)

	output = calculeNextOutput(state, debug=True)
	print(output[0] - 90, output[1], flush=True)
	print("step", step, ":", output, flush=True, file=sys.stderr)

	simule(state)

	draw.flush()
	step += 1