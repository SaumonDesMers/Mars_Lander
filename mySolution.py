import sys
import math
import os

class Draw:
	def __init__(self):
		self.cmd = []

	def line(self, x1, y1, x2, y2, width, color):
		self.cmd.append("LINE {} {} {} {} {} {}".format(int(x1), int(y1), int(x2), int(y2), int(width), color))

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
		xAcc = math.cos(math.radians(nextRotate)) * nextPower
		yAcc = math.sin(math.radians(nextRotate)) * nextPower - 3.711
		nextHSpeed = self.hSpeed + xAcc
		nextVSpeed = self.vSpeed + yAcc
		nextX = self.x + self.hSpeed + xAcc / 2
		nextY = self.y + self.vSpeed + yAcc / 2
		nextFuel = self.fuel - nextPower
		return State(nextX, nextY, nextHSpeed, nextVSpeed, nextFuel, nextRotate, nextPower)
	
	def nexts(self, inputList):
		stateList = []
		for input in inputList:
			state = self.next(input[0], input[1])
			stateList.append(state)
		return stateList

	def checkValue(self, x, y, hSpeed, vSpeed, fuel, rotate, power):
		return (
			round(self.x) == x
			and round(self.y) == y
			and round(self.hSpeed) == hSpeed
			and round(self.vSpeed) == vSpeed
			and round(self.fuel) == fuel
			and round(self.rotate) == rotate
			and round(self.power) == power
		)

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
			round(self.x),
			round(self.y),
			round(self.hSpeed),
			round(self.vSpeed),
			round(self.fuel),
			round(self.rotate - 90),
			round(self.power)
		)

def round(n):
	return int(n + (0.5 if n > 0 else -0.5))

def crossLand(state, prevState):
	global land
	if prevState is None:
		return None
	for i in range(len(land) - 1):
		# find the equation of the line
		# y = ax + b
		a = (land[i + 1][1] - land[i][1]) / (land[i + 1][0] - land[i][0])
		b = land[i][1] - a * land[i][0]
		# find the equation of the state line
		# y = cx + d
		c = 0 if state.x == prevState.x else (state.y - prevState.y) / (state.x - prevState.x)
		d = state.y - c * state.x
		# find the intersection point
		if a == c:
			continue
		x = (d - b) / (a - c)
		y = a * x + b
		if ((prevState.y <= y <= state.y or prevState.y >= y >= state.y)
			and (prevState.x <= x <= state.x or prevState.x >= x >= state.x)
			and (land[i][0] <= x <= land[i + 1][0] or land[i][0] >= x >= land[i + 1][0])
			and (land[i][1] <= y <= land[i + 1][1] or land[i][1] >= y >= land[i + 1][1])):
			return (x, y)
	return None

def outOfBounds(state):
	return state.x < 0 or state.x > 6999 or state.y < 0 or state.y > 2999

def hasLanded(s, offset=0):
	global landingSurface
	return (
		s.y <= landingSurface["y"]
		and landingSurface["x1"] + offset <= s.x <= landingSurface["x2"] - offset
		and abs(s.hSpeed) <= 20
		and abs(s.vSpeed) <= 40
		and s.rotate == 90
	)

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

def computeOutput(s, debug=False):

	ns_idle = s.next(s.rotate, state.power)

	act_vec = (s.hSpeed, s.vSpeed)

	dest_point = landingPoint(s)
	if landingSurface["x1"] > s.x or s.x > landingSurface["x2"]:
		dest_point = (dest_point[0], 3000)

	wish_vec = (dest_point[0] - ns_idle.x, dest_point[1] - ns_idle.y)
	wish_vec = normalize(wish_vec, max(norme(act_vec), 20))

	corr_vec = (wish_vec[0] - act_vec[0], wish_vec[1] - act_vec[1])

	output = getOutput(*corr_vec)
	tOutput = truncOutput(*output)
		
	ns = s.next(*tOutput)
	if debug:
		size = 5
		act_vec = (act_vec[0] * size, act_vec[1] * size)
		wish_vec = (wish_vec[0] * size, wish_vec[1] * size)
		corr_vec = (corr_vec[0] * size, corr_vec[1] * size)
		draw.line(ns.x, ns.y, ns.x + act_vec[0], ns.y + act_vec[1], 2, "#00ff00")
		draw.line(ns.x, ns.y, ns.x + wish_vec[0], ns.y + wish_vec[1], 2, "#0000ff")
		draw.line(ns.x, ns.y, ns.x + corr_vec[0], ns.y + corr_vec[1], 2, "#ff0000")
		draw.point(dest_point[0], dest_point[1], 10, "#ffff00")

		_x = ns.x + math.cos(math.radians(output[0])) * output[1]
		_y = ns.y + math.sin(math.radians(output[0])) * output[1]
		draw.line(ns.x, ns.y, _x, _y, 2, "#00ffff")
	
	return tOutput

def computeLanding(s, debug=False):
	power = 0
	if s.vSpeed < -30:
		power = 4
	return (90, power)

def oposingVector(s, debug=False):
	act_vec = (s.hSpeed, s.vSpeed)

	# dest_point = (3000, 1500)
	dest_point = landingPoint(s)

	# wish_vec = (dest_point[0] - ns_idle.x, dest_point[1] - ns_idle.y)
	wish_vec = (0, 3) # maybe 4
	# wish_vec = normalize(wish_vec, 20)

	corr_vec = (wish_vec[0] - act_vec[0], wish_vec[1] - act_vec[1])

	output = getOutput(*corr_vec)
	tOutput = truncOutput(*output)

	return tOutput

def simuleIdle(s, rotate, power):
	global step
	s = s.next(rotate, power)
	while True:
		if hasLanded(s):
			return True
		if outOfBounds(s) or crossLand(s):
			return False
		draw.line(s.x, s.y, s.x + s.hSpeed, s.y + s.vSpeed, 1, "#005555")
		draw.point(s.x, s.y, 5, "#777777")
		s = s.next(rotate, power)

def simule(s, _computeOutput, simuleLanding, debug=False, color="#555555"):
	global step
	output = _computeOutput(s)
	s = s.next(*output)
	ps = None
	while True:

		if hasLanded(s, 100):
			return True
		if outOfBounds(s) or crossLand(s, ps):
			return False
		
		if debug:
			draw.line(s.x, s.y, s.x + s.hSpeed, s.y + s.vSpeed, 1, color)
			draw.point(s.x, s.y, 5, color)

		if simuleLanding and abs(s.hSpeed) <= 20 and simule(s, computeLanding, simuleLanding=False, debug=not simuleValide, color="#606000"):
			output = computeLanding(s)
		else:
			output = _computeOutput(s)

		ps = s
		s = s.next(*output)


draw = Draw()

# retrieve lands points
surface_n = int(input())
land = []
for i in range(surface_n):
	land_x, land_y = [int(j) for j in input().split()]
	land.append((land_x, land_y))

# get landing surface
landingSurface = (0, 0, 0)
for i in range(surface_n - 1):
	if land[i][1] == land[i+1][1]:
		landingSurface = {
			"x1": land[i][0], 
			"x2": land[i+1][0],
			"y": land[i][1]
		}

funcComputeOutput = computeOutput
simuleValide = False
state = State(*[0]*7)

step = 1
while True:
	x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]

	# check if the compute state match the input state
	if not state.checkValue(x, y, h_speed, v_speed, fuel, rotate + 90, power):
		print("Change state to match input", file=sys.stderr, flush=True)
		state = State(x, y, h_speed, v_speed, fuel, rotate + 90, power)


	print("Step", step, file=sys.stderr, flush=True)
	print("  ", state, file=sys.stderr, flush=True)

	if not simuleValide and simule(state, computeOutput, simuleLanding=True, debug=True, color="#700000"):
		print("Base mode valide", flush=True, file=sys.stderr)
		simuleValide = True
	if funcComputeOutput != computeLanding and simule(state, computeLanding, simuleLanding=False, debug=True, color="#007070"):
		print("Switch to landing mode", flush=True, file=sys.stderr)
		funcComputeOutput = computeLanding
		simuleValide = True
	if not simuleValide and simule(state, oposingVector, simuleLanding=True, debug=True, color="#700070"):
		print("Switch to oposing vector mode", flush=True, file=sys.stderr)
		funcComputeOutput = oposingVector
		simuleValide = True
	
	simule(state, funcComputeOutput, simuleLanding=False, debug=True)
	output = funcComputeOutput(state, debug=True)

	print(output[0] - 90, output[1], flush=True)
	print("  ", output, flush=True, file=sys.stderr)

	state = state.next(*output)
	draw.flush()
	step += 1