import sys

sys.stdin = open("test.txt", "r")
sys.stdout = open("test2.txt", "w")

def gnl():
	while True:
		line = sys.stdin.readline().strip()
		if line:
			print(line, flush=True)
			return line

while gnl():
	pass