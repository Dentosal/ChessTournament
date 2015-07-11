import chess
import subprocess
import threading

TIMEOUT = 1 # seconds

class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None

	def run(self, input_string, timeout):
		""" Run command with timeout."""
		self.output = ""
		def target():
			self.process = subprocess.Popen(self.cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
			self.output = self.process.communicate(input_string)[0]

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			print 'Timeout -> Terminating process'
			self.process.terminate()
			thread.join()
		return [(self.process.returncode == 0), self.output]

class Bot:
	def __init__(self, name, executable):
		self.name = name
		self.executable = executable
		self.results = {"win": 0, "lost": 0, "draw": 0}
		self.command = Command("./"+self.executable)
	def decide(self, fen, moves, history):
		x = self.command.run(str(fen)+"\n"+str(moves)+"\n"+" ".join(history)+"\n", TIMEOUT)
		if not x[0]:	# timeout or program crash (or permission problem)
			print "Non-zero return code. '"+self.executable+"'"
			if True:	# AI debug
				print "VVV ERROR MSG VVV"
				print x[1]
				print "^^^^^^^^^^^^^^^^^"

			x = moves.split()[0]
			logs = []
		else:
			xq = [i.strip() for i in x[1].split("\n") if i.strip() != ""]
			logs = [i.split(": ", 1)[1].replace(";", "").replace("\n", "") for i in xq if i.split(": ")[0].lower() == "log"]
			xq = [i for i in xq if not ":" in i]
			if len(xq) != 1: # zero or multiple moves ~= illegal move
				print "Illegal move: ", xq
				x = moves.split()[0]
			else:
				x = x[1].strip()
		if not x in moves:  # illegal move
			print "Illegal move:", x
			x = moves.split()[0]
		return x, logs

class Game:
	def __init__(self, bots):
		self.bots = bots
		self.board = chess.Board("rnbqkbnr/pppppppp/8/8/P1QRKBN1/8/1PPPPPPP/1N3B1R w - - 0 1")
		self.move_history = []
		self.status = "running"
		# decide white and black
		self.white = bots[0]
		self.black = bots[1]
	def step(self):
		# get move
		fen =  self.board.fen()
		moves = " ".join([self.board.san(i) for i in self.board.generate_legal_moves()])
		current = {"w": self.white, "b": self.black}[fen.split()[1]]
		move, logmsgs = current.decide(fen, moves, self.move_history)
		self.board.push_san(move)
		self.move_history.append(move)
		# draw detect
		if self.board.is_insufficient_material():
			print "Draw: insufficient material"
			self.status = "draw"
			return "draw", logmsgs
		if self.board.is_stalemate():
			print "Draw: stalemate"
			self.status = "draw"
			return "draw", logmsgs
		if self.board.is_fivefold_repetition():
			print "Draw: fivefold repetition"
			self.status = "draw"
			return "draw", logmsgs
		if self.board.is_seventyfive_moves():
			print "Draw: seventyfive moves rule"
			self.status = "draw"
			return "draw", logmsgs
		if self.board.is_game_over():
			print "Check Mate"
			self.status = "win"
			return "win", logmsgs
		return None, logmsgs
