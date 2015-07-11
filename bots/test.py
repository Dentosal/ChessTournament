#!/usr/bin/env python2
fen = raw_input().split()
moves = raw_input().split()
history = raw_input().split()

import random, sys

captures = [i for i in moves if "x" in i]
if captures != []:
	print captures[0]
	sys.exit(0)
print random.choice(moves)
sys.exit(0)
