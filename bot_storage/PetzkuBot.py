#!/usr/bin/env python2
# coding=utf-8

"""First bot. Made for Dentosal's chess bot competition.

Rules:
1. Program recieves two lines of input.
1.1 The first line consists of the Forsyth–Edwards Notation
	representation of the game
1.2 The second line has all the possible moves in the situation
	in Standard Algebraic Notation, separated by spaces.
2. Program shall output the move it makes in the situation and exit.
2.1 Program must always make the same move in a given situation.
2.2 If the program doesn't give its move within 1 second,
	a move will be decided for it.

Description:
Prioritizes checkmates, then any captures, then any promotions,
finally any checks. Captures also prioritize promotions and checks,
and promotions prioritize checks.
If nothing else is available, program picks third available move.
This loops around if necessary.
Never underpromotes unless check or mate is available.

Made by Petteri Huuskonen (Petzku).
Contact:
	email: phuuskonen@paivola.fi
	IRC: Petzku @ PVLNet (irc.paivola.fi)

Copyright 2015 Petteri Huuskonen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys

fen = raw_input().split()
moves = raw_input().split()

# checkmate
for q in [q for q in moves if "#" in q]:
	print q
	sys.exit()

# capture
with [q for q in moves if "x" in q] as capts:
	with [q for q in capts if "=" in q] as prom_capts:
		for q in [q for q in prom_capts if "+" in q]:
			print q
			sys.exit()
		# no checks by promotion
		for q in [q for q in prom_capts if "Q" in q]:
			print q
			sys.exit()
	# no promotions by capture

# nothing else available
print moves[3%len(moves)]
