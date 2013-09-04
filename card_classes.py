

import random

class Deck():
	cards = []
	
	def __init__(self):
		for i in range(0, 4):
			for j in range(0, 13):
				self.cards.append((i,j))
				
		self.shuffle_deck()	
	
	def shuffle_deck(self):
		random.shuffle(self.cards)
			
	def reset_deck(self):
		self.__init__()
			
	def pop_cards(self, no_of_cards):
		card_list = []
		for i in range(0, no_of_cards):
			card = self.cards.pop(0)
			card_list.append(card)

		return card_list

class Hand():
	cards = []
	
	def insert_hand(self, hand):
		self.cards = hand 

class Card():
	backwards = False
	
	location = "" # DECK, TABLE OR PLAYER
	x_c = 0
	y_c = 0
	
	def __init__(self):
		self.location = "DECK"
	
	def flip_card(self):
		self.backwards = -self.backwards
		
	def change_location(self, where):
		self.location = where
		
	def change_coordinates(self, y, x):
		self.x_c = x
		self.y_c = y
