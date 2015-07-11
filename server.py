from twisted.web import server, resource
from twisted.internet import reactor, task
from twisted.web.resource import Resource

import os
import sys
import time
import itertools
from random import shuffle as rs

import game


GAME_STEP_INTERVAL = 1.5	# seconds
NEXT_GAME_DELAY = 3 # seconds

def getfile(filename):
	try:
		with open(filename) as fo:
			return fo.read()
	except:
		print "Error: File not found"
		return "<html><head><title>ERROR</title></head><body><tt>ERROR: FILE NOT FOUND</tt></body></html>"

def apireq(args):
	global current_game, nextgame_counter
	if len(args)==0:
		return "Error: Empty API Request"
	if args[0] == "ping":	# ping
		return "pong"
	elif args[0] == "game":	# full game status (including fen string)
		if current_game == None:
			return "waiting\n"+str(nextgame_counter)
		else:
			ret = "\n".join(["running",
								current_game.white.name,
								current_game.black.name,
								current_game.board.fen(),
								";".join(current_game.move_history)])
			return ret
	elif args[0] == "debug":
		if args[1] == "next":
			current_game = None
			nextgame_counter = 3
			return "OK"
		else:
			return "Error: Invalid API Request"
	else:
		return "Error: Invalid API Request"

class ChessGameServer(resource.Resource):
	isLeaf = True
	def render_GET(self, request):
		if request.uri == "/":
			return getfile("web/index.html")
		elif request.uri.startswith("/api/"):
			args = request.uri.split("/")[2:]
			return apireq(args)
		else:
			if ".." in request.uri:	# security
				print "Security Error"
				return "Security Error"
			return getfile("web"+request.uri)

def step():
	global current_game, nextgame_counter
	if current_game == None:
		if nextgame_counter > 0:
			nextgame_counter -= GAME_STEP_INTERVAL
			return
		else:
			nextgame_counter = 0

		if len(games) == 0:
			print "Done."
			reactor.stop()
			sys.exit(0)
		current_game = games[0]
		del games[0]

	if current_game.status in ["draw", "win"]:
		current_game = None
		nextgame_counter = 10
		return

	ret = current_game.step()
	if ret in ["draw", "win"]:
		status = ret


if __name__=="__main__":
	# fix bot permissions
	os.system("chmod u+x bots/*")

	# create games. every bot plays agains every bot, including itself and every game is played two times with different colors
	games = []
	for g in itertools.product([i for i in os.listdir("bots") if i[0]!="."], repeat = 2):
		games.append(game.Game([game.Bot(g[0].split(".")[0], "bots/"+g[0]), game.Bot(g[1].split(".")[0], "bots/"+g[1])]))

	rs(games)
	# debug: drop a is b games
	games = [i for i in games if i.white.name != i.black.name]

	status = "running"
	current_game = None
	nextgame_counter = NEXT_GAME_DELAY


	task.LoopingCall(step).start(GAME_STEP_INTERVAL, True)
	reactor.listenTCP(8080, server.Site(ChessGameServer()))
	reactor.run()
