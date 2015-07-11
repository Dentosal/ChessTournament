#!/usr/bin/env python2
import sys
fen = raw_input().split()
moves = raw_input().split()

board, my_color, castling, en_passant, halfmove_clock, fullmove_number = fen
halfmove_clock = int(halfmove_clock)
fullmove_number = int(fullmove_number)

if my_color == "w":
	start_table = ["e4", "d4", "Nc3", "Nf3"]
else:
	start_table = ["e5", "d5", "Nc6", "Nf6"]

print "log:", moves

mates = [i for i in moves if "#" in i]
if mates != []:
	print mates[0]
	sys.exit(0)
checks = [i for i in moves if "+" in i and "x" in i]
if checks != []:
	print checks[0]
	sys.exit(0)
promotions = [i for i in moves if "=" in i]
if promotions != []:
	# always queen
	promotions = [i for i in promotions if i[i.find("=")+1] in "qQ"]
	# promote by capturing
	promotions_with_capture = [i for i in promotions if "x" in i]
	if promotions_with_capture != []:
		print promotions_with_capture[0]
		sys.exit(0)
	# promote with check?
	promotions_with_check = [i for i in promotions if "+" in i]
	if promotions_with_check != []:
		print promotions_with_check[0]
		sys.exit(0)
	print promotions[0]
	sys.exit(0)

captures = [i for i in moves if "x" in i]
if captures != []:
	print captures[0]
	sys.exit(0)
checks = [i for i in sorted(moves, key=(lambda x: len(x))) if "O-O" in i]
if checks != []:
	print checks[0]
	sys.exit(0)

if fullmove_number < 20:
	for i in moves:
		if i in start_table:
			print i
			sys.exit(0)

if fullmove_number % 3 == 0:
	check = [i for i in moves if "+" in i]
	if check != []:
		print check[0]
		sys.exit(0)

print moves[0]
