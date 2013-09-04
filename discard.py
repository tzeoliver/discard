import gevent.monkey
gevent.monkey.patch_all()

import bottle
import socketio.server
import socketio.namespace
import socketio.mixins

import card_classes
import player_classes

from threading import Lock

class CardNamespace(socketio.namespace.BaseNamespace, socketio.mixins.BroadcastMixin):	
	players = []
	deck = card_classes.Deck()
	deck_mutex = Lock()
	game_initialized = False

	def initialize(self):
		if CardNamespace.game_initialized == False: 
			CardNamespace.deck.shuffle_deck()
			game_initialized = True
		print "initialized"

	def on_move(self, position):
		print "Position", position
		self.broadcast_event_not_me("move", position)

	def on_backfacing(self, backfacing):
		print "Backfacing", backfacing
		self.broadcast_event_not_me("backfacing", backfacing)
		CardNamespace.reset_deck()
		
	def on_request_cards(self, card_number):
		print "card requested"
		CardNamespace.deck_mutex.acquire()
		cards = CardNamespace.deck.pop_cards(card_number)
		CardNamespace.deck_mutex.release()
		print cards
		self.emit("request_cards", cards)
		
	def on_registration(self):
		# New player is entering the game, creating an id and sending it back
		print "stubbi"
		

@bottle.route("/socket.io/<remaining:path>")
def socketIO(remaining):
    print "Socket.io request"
    socketio.socketio_manage(bottle.request.environ, {'': CardNamespace}, bottle.request)

@bottle.route("/")
@bottle.route("/<file:path>")
def static(file="index.html"):
    print "Serving file", file
    return bottle.static_file(file, root="static")

bottle.debug()
socketio.server.SocketIOServer(("", 8000), bottle.app()).serve_forever()
