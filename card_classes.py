

import random

class Deck():		
	def __init__(self):		
		self.cards = []
		self.initialize_deck()
		
	def initialize_deck(self):
		# initializing cards and shuffling the deck		
		for i in range(0, 4):
			for j in range(0, 13):
				self.cards.append(Card(i,j))
				
		self.shuffle_deck()	
	
	def shuffle_deck(self):
		random.shuffle(self.cards)
			
	def reset_deck(self):
		self.initialize_decks()
			
	def pop_cards(self, no_of_cards, player_id):
		card_list = []
		for i in range(0, no_of_cards):
			card = self.cards.pop(0)
			card_list.append(card)

		return card_list
		
	def insert_cards(self, card_list):
		for i in range(0, len(card_list)):
			self.cards.append(card_list[i])
					
class Hand():
	
	def __init__(self):
		self.cards = []
		
	def insert_card(self, card):
		self.cards.append(card)
		
	def remove_card(self, suit_value_pair):
		for i in range(0, len(self.cards):
			if suit_value_pair == self.cards[i].get_suit_and_value():
				card = self.cards.pop(i)
				return card

class Card():
	# alternatives for location of the card
	DECK = 0
	PLAYER = 1
	TABLE = 2
	
	def __init__(self, c_suit, c_value):		
		self.suit = c_suit
		self.value = c_value
		self.backwards = False		
		self.location = DECK
		self.x_c = 0
		self.y_c = 0
	
	def flip_card(self):
		self.backwards = -self.backwards
		
	def change_location(self, where):
		self.location = where
		
	def change_coordinates(self, y, x):
		self.x_c = x
		self.y_c = y
		
	def get_suit_and_value(self):
		pair = (self.suit, self.value)
		return pair
