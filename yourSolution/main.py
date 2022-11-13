import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

surface_n = int(input())  # the number of points used to draw the surface of Mars.
for i in range(surface_n):
    # land_x: X coordinate of a surface point. (0 to 6999)
    # land_y: Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
    land_x, land_y = [int(j) for j in input().split()]

# game loop
while True:
	# h_speed: the horizontal speed (in m/s), can be negative.
    # v_speed: the vertical speed (in m/s), can be negative.
    # fuel: the quantity of remaining fuel in liters.
    # rotate: the rotation angle in degrees (-90 to 90).
    # power: the thrust power (0 to 4).
	x, y, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]

	# to debug: print("Debug messages...", file=sys.stderr, flush=True)

    # rotate power. rotate is the desired rotation angle. power is the desired thrust power.
	print("0 4")


	# Write the number of drawing commands that will follow
	print("0")

	# All the numbers must be integers.
	# The color must respect the format '#RRGGBB' (not case sensitive).

	# Draw a line from point A to point B with a width of W and a color of C.
	# print("LINE Ax Ay Bx By W C")

	# Draw a circle centered on point A with a radius of R and a color of C.
	# print("CIRCLE Ax Ay R C")

	# Draw a point at point A with a width of W and a color of C.
	# print("POINT Ax Ay W C")

	# I strongly recommend you to create a object that will handle the drawing commands.
	# One that stores the commands and then prints them all at once for example.
