
from card_classes import *

class Player:
	name = ""
	hand = Hand()
	
	def __init__(self, cards):
		hand.insert_hand(cards)
