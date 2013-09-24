import gevent.monkey
gevent.monkey.patch_all()

import bottle
import socketio.server
import socketio.namespace
import socketio.mixins

from threading import Lock

import card_classes
import player_classes


TABLE = 0
DECK = 1

class CardNamespace(socketio.namespace.BaseNamespace, socketio.mixins.BroadcastMixin):
	players = []
	player_mutex = Lock()

	deck = card_classes.Deck()
	deck_mutex = Lock()

	table = card_classes.CardHolder()
	table_mutex = Lock()

	id_numbers = []
	id_mutex = Lock()

	game_initialized = False

	def initialize(self):
		if CardNamespace.game_initialized == False:
			CardNamespace.deck.shuffle_deck()
			game_initialized = True

			# initializing id's (0 is reserved for the table, 1 for the deck)
			for i in range(2, 51):
				CardNamespace.id_numbers.append(i)

		print "initialized"

	def on_move(self, position):
		print "Position", position
		self.broadcast_event_not_me("move", position)

	def on_backfacing(self, backfacing):
		print "Backfacing", backfacing
		self.broadcast_event_not_me("backfacing", backfacing)

	def on_reset_game(self):
		# resets game --> initializes deck and removes cards from players
		CardNamespace.player_mutex.acquire()
		CardNamespace.deck_mutex.acquire()

		CardNamespace.deck.initialize_deck()
		for i in range(len(CardNamespace.players)):
			CardNamespace.players[i].reset_hand()

		CardNamespace.deck_mutex.release()
		CardNamespace.player_mutex.release()

		self.broadcast_event_not_me("reset")

	def on_shuffle_deck(self, player_id):
		CardNamespace.deck_mutex.acquire()
		CardNamespace.deck.shuffle_deck()
		CardNamespace.deck_mutex.release()
		self.broadcast_event_not_me("shuffle_deck", player_id)

	def on_change_card_location(self, old_and_new_id, card_suit_value):
		# takes the card from the old_and_new_id[0] and gives it to ...[1]

		# Searching the source and destination players
		CardNamespace.player_mutex.acquire()
		CardNamespace.deck_mutex.acquire()
		CardNamespace.table_mutex.acquire()

		source = None
		destination = None

		for i in range(len(CardNamespace.players)):
			if CardNamespace.players[i].get_id() == old_and_new_id[0]:
				source = CardNamespace.players[i].get_hand()
			elif CardNamespace.players[i].get_id() == old_and_new_id[1]:
				destination = CardNamespace.players[i].get_hand()

			if source != None and destination != None:
				break

		# If the source is not a player, it could be the table
		if source == None:
			if old_and_new_id[0] == TABLE:
				source = CardNamespace.table
			else:
				print "unknown source"
				self.emit("on_change_card_location", -1)
				return

		# If the destination is not a player, it could be either table or deck
		if destination == None:
			if old_and_new_id[1] == TABLE:
				destination = CardNamespace.table
			elif old_and_new_id[1] == DECK:
				destination = CardNamespace.deck
			else:
				print "unknown destination"
				self.emit("on_change_card_location", -1)
				return

		# Taking the card from the source...
		card = source.pop_card(card_suit_value)

		if card == -1:
			# The card couldn't be found from the source player
			CardNamespace.player_mutex.release()
			CardNamespace.deck_mutex.release()
			CardNamespace.table_mutex.release()
			self.emit("on_change_card_location", -1)
			return

		# ...and inserting it to the destination
		destination.get_hand().insert_card(card)

		CardNamespace.player_mutex.release()
		CardNamespace.deck_mutex.release()
		CardNamespace.table_mutex.release()

		# TODO: Informing players that the card's location has been changed

	def on_flip_card(self, id_number, card_suit_value):
		CardNamespace.player_mutex.acquire()
		for i in range(len(CardNamespace.players)):
			if CardNamespace.players[i].get_id() == id_number:
				CardNamespace.players[i].get_hand().get_card(card_suit_value).flip_card()
		CardNamespace.player_mutex.release()

		# If the card has been flipped on the table (id == 0), broadcasting event
		if id_number == TABLE:
			print "broadcast must be made"


	def on_request_cards(self, id_number, card_number):
		# Searching for a right player based on the received id
		player = None
		CardNamespace.player_mutex.acquire()
		for i in range(len(CardNamespace.players)):
			if CardNamespace.players[i].get_id() == id_number:
				player = CardNamespace.players[i]

		if player == None:
			self.emit("request_cards", -1)
			CardNamespace.player_mutex.release()
			return

		# Taking cards from the deck and moving them to the player
		CardNamespace.deck_mutex.acquire()
		cards = CardNamespace.deck.pop_cards(card_number)
		CardNamespace.deck_mutex.release()

		if cards == -1:
			self.emit("request_cards", -1)
			CardNamespace.player_mutex.release()
			return

		player.get_hand().insert_cards(cards)
		CardNamespace.player_mutex.release()

		# Constructing a list of (suit, value) tuples and sending them back to the player
		card_tuple_list = []
		for i in range(len(cards)):
			card_tuple_list.append(cards[i].get_suit_and_value())

		print card_tuple_list
		self.emit("request_cards", card_tuple_list)

	def on_registration(self):
		# New player is entering the game, taking id from the pool and sending it back
		CardNamespace.id_mutex.acquire()
		taken_id = CardNamespace.id_numbers.pop(0)
		CardNamespace.id_mutex.release()

		CardNamespace.players.append(player_classes.Player(taken_id))
		self.emit("registration", taken_id)
		print taken_id

	def on_quit(self, player_id):
		# removing player from the list
		CardNamespace.player_mutex.acquire()
		for i in range(len(CardNamespace.players)):
			if CardNamespace.players[i].get_id() == player_id:
				CardNamespace.players.pop(i)
		CardNamespace.player_mutex.release()

		# inserting id number back to the list
		CardNamespace.id_mutex.acquire()
		CardNamespace.id_numbers.append(player_id)
		CardNamespace.id_mutex.release()

@bottle.route("/socket.io/<remaining:path>")
def socketIO(remaining):
	print "Socket.io request"
	#cns = CardNamespace()
	#cns.add_session(bottle.request.environ.get('beaker.session'))
	socketio.socketio_manage(bottle.request.environ, {'': CardNamespace}, bottle.request)
	#socketio.socketio_manage(bottle.request.environ, {'': cns}, bottle.request)

@bottle.route("/")
@bottle.route("/<file:path>")
def static(file="index.html"):
	print "Serving file", file
	return bottle.static_file(file, root="static")

bottle.debug()
socketio.server.SocketIOServer(("", 8000), bottle.app()).serve_forever()
#socketio.server.SocketIOServer(("", 8000), app).serve_forever()
