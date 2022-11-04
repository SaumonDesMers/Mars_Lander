import math
import os
import re
import sys
import time
import subprocess
import select
import threading

class State:
	def __init__(self, x, y, hSpeed, vSpeed, fuel, rotate, power):
		self.x = x
		self.y = y
		self.hSpeed = hSpeed
		self.vSpeed = vSpeed
		self.fuel = fuel
		self.rotate = rotate
		self.power = power
		self.draw = []
	
	def dict(self):
		return {
			"x": int(self.x),
			"y": int(self.y),
			"hSpeed": int(self.hSpeed),
			"vSpeed": int(self.vSpeed),
			"fuel": int(self.fuel),
			"rotate": int(self.rotate),
			"power": int(self.power),
			"draw": self.draw
		}

def gnl(io, timeout=1):
	# print("Game waiting for input...", file=sys.stderr, flush=True)
	start = time.time()
	while time.time() - start < timeout:
		line = io.readline().strip()
		if line:
			# print("Game read: {}".format(line), file=sys.stderr, flush=True)
			return line
	global player
	player.kill()
	error("timeout")
	exit(1)

def gnl_timeout(io, timeout=1):
	select_obj = select.select([io], [], [], timeout)[0]
	if select_obj:
		return io.readline().strip()
	else:
		global player
		player.kill()
		error("timeout")
		exit(1)

def gnl_thread(io, timeout=1) -> str:

	def get_line(line):
		line[0] = io.readline().strip()

	line = [None]
	t = threading.Thread(target=get_line, args=(line))
	t.start()
	t.join(timeout)
	if t.is_alive():
		
		global player
		player.kill()
		error("timeout")
		exit(1)
	else:
		return line[0]


def error(msg):
	print("\033[91mError:\033[0m {}".format(msg), file=sys.stderr)

def cartToPolar(x, y):
	r = math.sqrt(x**2 + y**2)
	theta = math.atan2(y, x)
	return r, theta

def polarToCart(r, theta):
	x = r * math.cos(theta)
	y = r * math.sin(theta)
	return x, y

def crossLand(state):
	global land
	for i in range(len(land) - 1):
		if land[i]["x"] <= state.x <= land[i + 1]["x"]:
			# find the equation of the line
			# y = ax + b
			a = (land[i + 1]["y"] - land[i]["y"]) / (land[i + 1]["x"] - land[i]["x"])
			b = land[i]["y"] - a * land[i]["x"]
			return state.y <= a * state.x + b
	return False

def outOfBounds(state):
	return state.x < 0 or state.x > 6999 or state.y < 0 or state.y > 2999

def simule(data, program):
	global land
	land = data["land"]
	state = State(**data["start"])
	game = [state.dict()]

	# execute the program in a subprocess
	global player
	player = subprocess.Popen(
		["python3", program],
		stdout=subprocess.PIPE,
		stderr=sys.stderr,
		stdin=subprocess.PIPE
	)

	# send the surface to the program
	# print("Game sending surface...", file=sys.stderr, flush=True)
	player.stdin.write("{}\n".format(len(land)).encode())
	for i in range(data["surface_n"]):
		# print("Game sending surface point {}...".format(i), file=sys.stderr, flush=True)
		player.stdin.write("{} {}\n".format(land[i]["x"], land[i]["y"]).encode())

	while not crossLand(state) and not outOfBounds(state):

		# send the state to the program
		print("Game sending state...", file=sys.stderr, flush=True)
		player.stdin.write("{} {} {} {} {} {} {}\n".format(int(state.x), int(state.y), int(state.hSpeed), int(state.vSpeed), int(state.fuel), int(state.rotate), int(state.power)).encode())
		player.stdin.flush()

		# read input from stdin
		print("Game waiting for rotation and power...", file=sys.stderr, flush=True)
		str = gnl_thread(player.stdout).decode()
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

		# update the rotation and power
		state.rotate += min(15, max(-15, rotate - state.rotate))
		state.power += 1 if power > state.power else -1 if power < state.power else 0

		# update the state
		state.hSpeed += math.cos(math.radians(state.rotate - 90)) * power
		state.vSpeed += -math.sin(math.radians(state.rotate - 90)) * power - 3.711
		state.x += state.hSpeed
		state.y += state.vSpeed
		state.fuel -= power

		# read the draw command
		print("Game waiting for draw command...", file=sys.stderr, flush=True)
		draw_n = gnl_thread(player.stdout).decode()
		if not re.match(r"^\d+$", draw_n):
			error("invalid draw_n format")
			player.kill()
			exit(1)
		draw_n = int(draw_n)
		print("draw_n = "+draw_n, file=sys.stderr, flush=True)
		state.draw = []
		for i in range(draw_n):
			str = gnl_thread(player.stdout).decode()
			if re.match(r"LINE \d+ \d+ \d+ \d+ \d+ #\d{6}$", str):
				args = str.split(" ")
				state.draw.append({
					"type": "line",
					"x1": int(args[1]),
					"y1": int(args[2]),
					"x2": int(args[3]),
					"y2": int(args[4]),
					"width": int(args[5]),
					"color": args[6]
				})
			elif re.match(r"ELLIPSE \d+ \d+ \d+ \d+ \d+ #\d{6}$", str):
				args = str.split(" ")
				state.draw.append({
					"type": "ellipse",
					"x": int(args[1]),
					"y": int(args[2]),
					"width": int(args[3]),
					"height": int(args[4]),
					"width": int(args[5]),
					"color": args[6]
				})
			elif re.match(r"CIRCLE \d+ \d+ \d+ \d+ #\d{6}$", str):
				args = str.split(" ")
				state.draw.append({
					"type": "circle",
					"x": int(args[1]),
					"y": int(args[2]),
					"radius": int(args[3]),
					"width": int(args[4]),
					"color": args[5]
				})
			elif re.match(r"POINT \d+ \d+ \d+ #\d{6}$", str):
				args = str.split(" ")
				state.draw.append({
					"type": "point",
					"x": int(args[1]),
					"y": int(args[2]),
					"width": int(args[3]),
					"color": args[4]
				})
			else:
				error("invalid draw command")
				player.kill()
				exit(1)

		print(state.dict(), file=sys.stderr, flush=True)
		game.append(state.dict())
	
	player.kill()
	return game