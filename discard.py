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
	deck = card_classes.Deck()
	mutex = Lock()


	def initialize(self):
		CardNamespace.deck.shuffle_deck()
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
		CardNamespace.mutex.acquire()
		cards = CardNamespace.deck.pop_cards(card_number)
		CardNamespace.mutex.release()
		print cards
		self.emit("request_cards", cards)

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
