#!/usr/bin/env python2
# coding: ascii


# DentoBot, The Ultimate Chess AI
# Copyright (c) Hannes Karppila 2015
#
# Algorithms and methods:
#  Implemented:
#  Planned:
#   * Enemy simulation => Move prediction
#   * Position analysis => Minimax?
#   * Button value analysis => Trade worthiness detection?
#   * Move planning
#   * SAN analyzer
#   * Endgame scripts

import sys
import re

def done(m):
	print m
	sys.exit(0)

# hard-coded data
PIECE_VALUE = {"k": 4, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1}


# start
fen = raw_input()
raw_moves = raw_input().split()
history = raw_input().split()

fen_board, my_color, castling_permissions, en_passant, halfmove_clock, fullmove_number = fen.split()
halfmove_clock = int(halfmove_clock)
fullmove_number = int(fullmove_number)

# quick moves
if len(raw_moves) == 1:
	done(raw_moves[0])
for m in raw_moves:
	if "#" in m:
		done(m)

# classes
class Board:
	def __init__(self, fen):
		self.pieces = []
		self.turn = "w"
		self.castling_permissions = ""
		self.en_passant = ""
		self.init_fen(fen)
	def init_fen(self, fen):
		f = fen.split()
		# board
		x = 1
		y = 1
		for c in f[0]:
			if c in "12345678":
				x += int(c)
			elif c == "/":
				x = 1
				y += 1
			else:
				self.add(Piece(c, Coordinate(x, y)))
				x += 1
		# data
		self.turn = f[1]
		self.castling_permissions = f[2]
		self.en_passant = f[3]
		self.halfmove_clock = int(f[4])
		self.fullmove_number = int(f[5])
	def add(self, object):
		self.pieces.append(object)
	def get_at(self, pos):
		for p in self.pieces:
			if p.position == pos:
				return p
		return None
	def get_valid_moves(self):
		pass
	def get_pseudo_valid_moves_at(self, pos):
		piece = self.get_at(pos)
		if piece == None:
			return []
		print piece
		return piece.get_pseudo_valid_moves(self)
	def is_line_clear(self, start, end):
		start = [start[0], start[1]]
		end = [end[0], end[1]]
		if self.get_at(start) != None:
			return False
		while start != end:
			if start[1] != end[1]:
				if start[1] < end[1]:
					start[1] += 1
				else:
					start[1] -= 1
			if start[0] != end[0]:
				if start[0] < end[0]:
					start[0] += 1
				else:
					start[0] -= 1
			if self.get_at(start) != None:
				return False
		return True
	def scan_line(self, position, offset):
		position = Coordinate(position).moved(offset)
		clear = []
		while self.get_at(position) == None and position.is_valid():
			clear.append(position.copy())
			position = position.moved(offset)
		return clear
class Piece:
	def __init__(self, symbol, pos):
		self.color = "w" if symbol == symbol.upper() else "b"
		self.piece = symbol.lower()
		self.position = pos
	def get_value(self):
		return PIECE_VALUE[self.piece.lower()]
	def get_pseudo_valid_moves(self, board):
		ret = []
		if self.piece in "rq":
			ret += board.scan_line(self.position, [-1, 0])
			ret += board.scan_line(self.position, [0, -1])
			ret += board.scan_line(self.position, [1, 0])
			ret += board.scan_line(self.position, [0, 1])
		elif self.piece in "bq":
			ret += board.scan_line(self.position, [-1, -1])
			ret += board.scan_line(self.position, [-1, 1])
			ret += board.scan_line(self.position, [1, -1])
			ret += board.scan_line(self.position, [1, 1])
		elif self.piece == "k":
			for q in [-1, 0, 1]:
				for w in [-1, 0, 1]:
					if (not (w == 0 and q == 0)) and (board.get_at([q, w]) == None):
						ret += Coordinate([q, w])
		return ret
	def __repr__(self):
		return self.piece.lower() if self.color == "b" else self.piece.upper()

class Coordinate:
	def __init__(self, a, b=None):
		if type(a) == type(""):
			if re.findall("[a-h][1-8]", a)[0] == a:
				self.x = ord(a[0])-96
				self.y = int(a[1])
			elif len(a) == 1:
				if b in "12345678":
					b = int(b)
				if a[0] in "abcdefgh" and b in [1, 2, 3, 4, 5, 6, 7, 8]:
					self.x = ord(a[0])-96
					self.y = int(b)
				else:
					raise ValueError, "Invalid Coordinate"
			else:
				raise ValueError, "Invalid Coordinate"
		elif type(a) in [type([]), type((0,1))]:
			self.x = a[0]
			self.y = a[1]
		elif isinstance(a, Coordinate):
			self.x = a.x
			self.y = a.y
		elif type(a) == type(0) and type(b) == type(0):
			self.x = a
			self.y = b
		else:
			raise ValueError, "Invalid Coordinate"
	def moved(self, offset):
		return Coordinate([self.x-offset[0], self.y-offset[1]])
	def is_valid(self):
		return self.x in range(1, 9) and self.y in range(1, 9)
	def __repr__(self):
		return "Coordinate("+chr(96+self.x)+str(self.y)+")"
	def __getitem__(self, index):
		if index == 0:
			return self.x
		elif index == 1:
			return self.y
		else:
			raise ValueError
	def __eq__(self, other):
		return (other[0] == self[0] and other[1] == self[1])
	def copy(self):
		return Coordinate(self)

class Move:
	pass
class MoveFromSan(Move):
	def __init__(self, san, board):
		self.san = san
		# fast SAN searches
		self.check = "+" in self.san
		self.promotion = "=" in self.san
		self.mate = "#" in self.san
		# compute source from board
		self.init_coordinates(board)
	def init_coordinates(self, board):
		""" Convert SAN to two coordinates, from http://pwnedthegameofchess.com/san/ """
		source_f = -1
		source_r = -1
		dest_f = -1
		dest_r = -1
		ff = ""
		sf = ""
		fr = ""
		sr = ""
		promote = "Q"
		if self.san == "O-O":	# king side castle
			if board.turn == "b":
				dest_r = 8
				dest_f = 7
			else:
				dest_r = 1
				dest_f = 7
		elif self.san == "O-O-O": # queen side castle
			if board.turn == "b":
				dest_r = 8
				dest_f = 3
			else:
				dest_r = 1
				dest_f = 3
		else:
			for st in self.san:
				if st in "abcdefgh":	# is this a valid file
					# is this the first time the token is referencing a file?
					if ff == "":
						ff = st
					else:
						sf = st
				if st in "12345678":	# is this a valid rank
					# is this the first time the token is referencing a rank?
					if fr == "":
						fr = st
					else:
						sr = st
				if st in "BNR":
					promote = st
			# now figure out the source and dest rank and file based on what was in the SAN token
			if sf == "":
				dest_f = ord(ff.lower())-96
			else:
				source_f = ord(sf.lower())-96
				dest_f = ord(sf.lower())-96
			if sr == "":
				dest_r = int(fr)
			else:
				source_r = int(fr)
				dest_r = int(sr)
		if dest_r == -1 and dest_f == -1:
			raise ValueError, "Invalid SAN destination"

		self.dest = Coordinate([dest_f, dest_r])
		# ...
	def __repr__(self):
		return "Move("+self.san+")"


# init
board = Board(fen)
moves = [MoveFromSan(s, board) for s in raw_moves]


# smart SAN analysis
print "log:", "d4", board.get_at(Coordinate("d4"))
print "log:", "d5", board.get_at(Coordinate("d5"))
print "log:", Coordinate("d4").x, Coordinate("d4").y
# stupid SAN analysis

# select piece to move
done(moves[0])
