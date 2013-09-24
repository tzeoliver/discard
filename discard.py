import sys
sys.path.insert(0, "lib/gevent-0.13.8")
sys.path.insert(0, "lib/bottle")
sys.path.insert(0, "lib/gevent-socketio")

import random

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

	cards = {}
	deck = []
	table = []

	id_numbers = []
	id_mutex = Lock()

	initialized = False

	def initialize(self):
		if not CardNamespace.initialized:
			# initializing id's (0 is reserved for the table, 1 for the deck)
			for i in range(2, 51):
				CardNamespace.id_numbers.append(i)

			for i in range(0, 4):
				for j in range(1, 14):
					card = card_classes.Card(i, j)
					CardNamespace.cards[card.id] = card
					CardNamespace.deck.append(card)

			random.shuffle(CardNamespace.deck)

			for i, card in enumerate(CardNamespace.deck):
				card.x_c = 10 + i * 0.5
				card.y_c = 10 + i * 0.5

			CardNamespace.initialized = True

			print "initialized"

	def on_get_state(self):
		deck = []
		for card in CardNamespace.deck:
			deck.append(card.id)

		table = []
		for card in CardNamespace.table:
			table.append(card.id)

		cards = []
		for card in CardNamespace.cards.itervalues():
			cards.append({"id": card.id,
									  "x": card.x_c,
									  "y": card.y_c,
									  "backfacing": card.backwards})

		state = {"deck": deck,
						 "table": table,
						 "cards": cards}
		self.emit("set_state", state)

	def on_pop(self):
		print "pop"
		card = CardNamespace.deck.pop()
		CardNamespace.table.append(card)
		self.broadcast_event_not_me("pop")

	def on_start_drag(self, card_id):
		print "start_drag", card_id
		self.broadcast_event_not_me("start_drag", card_id)

	def on_end_drag(self, card_id):
		print "end_drag", card_id
		self.broadcast_event_not_me("end_drag", card_id)

	def on_move(self, card_id, x, y):
		#print "move", card_id, x, y
		card = self.cards[card_id]
		card.x_c = x
		card.y_c = y
		self.broadcast_event_not_me("move", card_id, x, y)

	def on_flip(self, card_id, backfacing):
		print "flip", card_id, backfacing
		self.cards[card_id].backwards = backfacing
		self.broadcast_event_not_me("flip", card_id, backfacing)

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
