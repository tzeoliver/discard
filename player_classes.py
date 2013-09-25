
from card_classes import *

class Player:
		
	def __init__(self, id_num):
		self.id_number = id_num
		self.hand = CardHolder()
		
	def get_hand(self):
		return self.hand
		
	def get_id(self):
		return self.id_number
		
	def reset_hand(self):
		self.hand.reset()
