import sys
import math
import os


# print("Player started", file=sys.stderr, flush=True)

def gnl():
	# print("Player waiting for input...", file=sys.stderr, flush=True)
	while True:
		line = sys.stdin.readline().strip()
		if line:
			# print("Player read: {}".format(line), file=sys.stderr, flush=True)
			return line

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

def normalize(vec, n=1):
	m = (1 / norme(vec)) * n
	return (vec[0] * m, vec[1] * m)

surface_n = int(gnl())
land = []
for i in range(surface_n):
	land_x, land_y = [int(j) for j in gnl().split()]
	land.append((land_x, land_y))

# get landing point
landingPoint = (0, 0)
for i in range(surface_n - 1):
	if land[i][1] == land[i+1][1]:
		landingPoint = (int(land[i][0] + (land[i+1][0] - land[i][0]) / 2), land[i][1])

while True:
	x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in gnl().split()]

	act_vec = (h_speed, v_speed+3.7)
	# print("vec actuel =", act_vec, file=sys.stderr, flush=True)

	wish_vec = (landingPoint[0] - x, landingPoint[1] - y)
	wish_vec = normalize(wish_vec, 20)
	# print("vec voulu =", wish_vec, file=sys.stderr, flush=True)

	corr_vec = (wish_vec[0] - act_vec[0], wish_vec[1] - act_vec[1])
	# print("vec correctionel =", corr_vec, file=sys.stderr, flush=True)

	output = truncOutput(*getOutput(*corr_vec))
	if y < landingPoint[1] + 2000:
		output = (0, output[1])
		
	# print("Player output: {}".format(output), file=sys.stderr, flush=True)
	print(*output, flush=True)
	# print("0 4", flush=True)
	print(0, flush=True)



# To debug: print("Debug messages...", file=sys.stderr, flush=True)