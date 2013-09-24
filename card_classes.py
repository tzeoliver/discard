

import random


class CardHolder():

	def __init__(self):
		self.cards = []

	def insert_card(self, card):
		self.cards.append(card)

	def insert_cards(self, card_list):
		for i in range(len(card_list)):
			self.cards.append(card_list[i])

	def pop_card(self, suit_value_pair):
		for i in range(0, len(self.cards)):
			if self.cards[i].get_suit_and_value() == suit_value_pair_list[i]:
				card = self.cards.pop(i)
				return card
		return -1

	def pop_specified_cards(self, suit_value_pair_list):
		card_index_list = []
		for i in range(0, len(self.cards)):
			if self.cards[i].get_suit_and_value() == suit_value_pair_list[i]:
				#card = self.cards.pop(i)
				#card_list.append(card)
				card_index_list.append(i)

		if len(suit_value_pair_list) != len(card_index_list):
			return -1
		else:
			card_list = []
			for i in range(len(card_index_list)):
				card_list.append(self.cards.pop(card_index_list[i]))
			return card_list

	def get_card(self, suit_value):
		for i in range(len(self.cards)):
			if self.cards[i].get_suit_and_value() == suit_value:
				return self.cards[i]

	def reset(self):
		self.cards = []

class Deck(CardHolder):
	def __init__(self):
		CardHolder.__init__(self)
		self.initialize_deck()

	def initialize_deck(self):
		# initializing cards and shuffling the deck
		self.reset()
		for i in range(0, 4):
			for j in range(0, 13):
				self.cards.append(Card(i, j))

		self.shuffle_deck()

		for i, card in enumerate(self.cards):
			card.x_c = i * 0.5
			card.y_c = i * 0.5

	def shuffle_deck(self):
		random.shuffle(self.cards)

	def reset_deck(self):
		self.initialize_decks()

	def pop_cards(self, no_of_cards):
		if no_of_cards > len(self.cards):
			return -1

		card_list = []
		for i in range(0, no_of_cards):
			card = self.cards.pop(0)
			card_list.append(card)

		return card_list

class Card():
	def __init__(self, c_suit, c_value):
		self.suit = c_suit
		self.value = c_value
		self.backwards = True
		self.x_c = 0
		self.y_c = 0

	@property
	def id(self):
		return "{}-{}".format(self.suit, self.value)

	def flip_card(self):
		self.backwards = -self.backwards

	def change_coordinates(self, y, x):
		self.x_c = x
		self.y_c = y

	def get_suit_and_value(self):
		pair = (self.suit, self.value)
		return pair
