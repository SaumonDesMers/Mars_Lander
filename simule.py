import math
import os
import re
import sys
import time
import subprocess

class State:
	def __init__(self, x, y, hSpeed, vSpeed, fuel, rotate, power):
		self.x = x
		self.y = y
		self.hSpeed = hSpeed
		self.vSpeed = vSpeed
		self.fuel = fuel
		self.rotate = rotate
		self.power = power
	
	def dict(self):
		return {
			"x": int(self.x),
			"y": int(self.y),
			"hSpeed": int(self.hSpeed),
			"vSpeed": int(self.vSpeed),
			"fuel": int(self.fuel),
			"rotate": int(self.rotate),
			"power": int(self.power),
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
		["python", program],
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
		# print("Game sending state...", file=sys.stderr, flush=True)
		player.stdin.write("{} {} {} {} {} {} {}\n".format(int(state.x), int(state.y), int(state.hSpeed), int(state.vSpeed), int(state.fuel), int(state.rotate), int(state.power)).encode())
		player.stdin.flush()

		# read input from stdin
		str = gnl(player.stdout).decode()
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
		state.hSpeed += math.cos(math.radians(state.rotate)) * power
		state.vSpeed += math.sin(math.radians(state.rotate)) * power - 3.711
		state.x += state.hSpeed
		state.y += state.vSpeed
		state.fuel -= power

		print(state.dict(), file=sys.stderr, flush=True)
		game.append(state.dict())
	
	player.kill()
	return game