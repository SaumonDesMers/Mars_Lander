import math
import os
import re
import sys
import time
import subprocess
import select
import threading
import queue

def error(msg):
	print("\033[91mError:\033[0m {}".format(msg), file=sys.stderr)

class NonBlockingStreamReader:
	def __init__(self, stream):
		self._s = stream
		self._q = queue.Queue()

		def _populateQueue(stream, queue):
			while True:
				line = stream.readline()
				if line:
					queue.put(line)
				else:
					# Either closed or blocked
					time.sleep(0.1)

		self._t = threading.Thread(target=_populateQueue, args=(self._s, self._q))
		self._t.daemon = True
		self._t.start()  # start collecting lines from the stream

	def readline(self, timeout=1):
		try:
			return self._q.get(block=timeout is not None, timeout=timeout)
		except queue.Empty:
			global player
			player.kill()
			error("Your program timed out.")
			sys.exit(1)

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
	
	def dict(self):
		return {
			"x": round(self.x),
			"y": round(self.y),
			"hSpeed": round(self.hSpeed),
			"vSpeed": round(self.vSpeed),
			"fuel": round(self.fuel),
			"rotate": round(self.rotate),
			"power": round(self.power),
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
		a = (land[i + 1]["y"] - land[i]["y"]) / (land[i + 1]["x"] - land[i]["x"])
		b = land[i]["y"] - a * land[i]["x"]
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
			and (land[i]["x"] <= x <= land[i + 1]["x"] or land[i]["x"] >= x >= land[i + 1]["x"])
			and (land[i]["y"] <= y <= land[i + 1]["y"] or land[i]["y"] >= y >= land[i + 1]["y"])):
			return (x, y)
	return None

def outOfBounds(state):
	return state.x < 0 or state.x > 6999 or state.y < 0 or state.y > 2999

def hasLanded(s, intersection):
	global landingSurface
	if intersection is None:
		return False
	return (
		intersection[1] <= landingSurface["y"]
		and landingSurface["x1"] <= intersection[0] <= landingSurface["x2"]
		and abs(int(s.hSpeed)) <= 20
		and abs(int(s.vSpeed)) <= 40
		and s.rotate == 90
	)

def simule(data, program):
	global land
	land = data["land"]
	data["start"]["rotate"] += 90
	state = State(**data["start"])
	prevState = None
	game = [state.dict()]

	# get landing surface
	global landingSurface
	landingSurface = (0, 0, 0)
	for i in range(len(land) - 1):
		if land[i]["y"] == land[i+1]["y"]:
			landingSurface = {
				"x1": land[i]["x"], 
				"x2": land[i+1]["x"],
				"y": land[i]["y"]
			}

	# execute the program in a subprocess
	global player
	player = subprocess.Popen(
		["python3", program],
		stdout=subprocess.PIPE,
		stderr=sys.stderr,
		stdin=subprocess.PIPE
	)

	# create a non-blocking reader for the subprocess
	io = NonBlockingStreamReader(player.stdout)

	# send the surface to the program
	# print("Game sending surface...", file=sys.stderr, flush=True)
	player.stdin.write("{}\n".format(len(land)).encode())
	for i in range(data["surface_n"]):
		# print("Game sending surface point {}...".format(i), file=sys.stderr, flush=True)
		player.stdin.write("{} {}\n".format(land[i]["x"], land[i]["y"]).encode())

	while True:

		intersection = crossLand(state, prevState)
		if hasLanded(state, intersection):
			print("\033[92mSuccess !\033[0m", file=sys.stderr, flush=True)
			break
		if outOfBounds(state) or intersection is not None:
			print("\033[91mFail !\033[0m", file=sys.stderr, flush=True)
			break

		# send the state to the program
		# print("Game sending state...", file=sys.stderr, flush=True)
		player.stdin.write("{} {} {} {} {} {} {}\n".format(
			round(state.x),
			round(state.y),
			round(state.hSpeed),
			round(state.vSpeed),
			round(state.fuel),
			round(state.rotate - 90),
			round(state.power)
		).encode())
		player.stdin.flush()

		# read input from stdin
		# print("Game waiting for rotation and power...", file=sys.stderr, flush=True)
		str = io.readline().decode()
		if not re.match(r"^[\d-]+ \d+$", str):
			error("invalid input format")
			player.kill()
			exit(1)
		
		rotate, power = map(int, str.split(" "))
		# check input values
		if not -90 <= rotate <= 90:
			error("invalid rotate value")
			player.kill()
			exit(1)
		if not 0 <= power <= 4:
			error("invalid power value")
			player.kill()
			exit(1)

		prevState = state
		state = state.next(rotate + 90, power)

		# read the draw command
		# print("Game waiting for draw command...", file=sys.stderr, flush=True)
		draw_n = io.readline().decode()
		if not re.match(r"^\d+$", draw_n):
			error("invalid number of draw command")
			player.kill()
			exit(1)
		draw_n = int(draw_n)
		state.drawCmd = []
		for i in range(draw_n):
			str = io.readline().decode()
			if re.match(r"LINE [\d-]+ [\d-]+ [\d-]+ [\d-]+ \d+ #[\da-fA-F]{6}$", str):
				args = str.split(" ")
				state.drawCmd.append({
					"type": "line",
					"x1": int(args[1]),
					"y1": int(args[2]),
					"x2": int(args[3]),
					"y2": int(args[4]),
					"width": int(args[5]),
					"color": args[6]
				})
			elif re.match(r"CIRCLE [\d-]+ [\d-]+ \d+ \d+ #[\da-fA-F]{6}$", str):
				args = str.split(" ")
				state.drawCmd.append({
					"type": "circle",
					"x": int(args[1]),
					"y": int(args[2]),
					"radius": int(args[3]),
					"width": int(args[4]),
					"color": args[5]
				})
			elif re.match(r"POINT [\d-]+ [\d-]+ \d+ #[\da-fA-F]{6}$", str):
				args = str.split(" ")
				state.drawCmd.append({
					"type": "point",
					"x": int(args[1]),
					"y": int(args[2]),
					"width": int(args[3]),
					"color": args[4]
				})
			else:
				error("invalid draw command: {}".format(str))
				player.kill()
				exit(1)

		# print("game  ", state, file=sys.stderr, flush=True)
		game.append(state.dict())
	
	player.kill()
	return game