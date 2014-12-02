from core.card import *

class Table(object):

    def __init__(self, mental_poker):
        self.__mental_poker = mental_poker

        self.players = []
        self.cards = []


    def deal_cards(self):
        deck = create_deck()
        self.cards = self.__mental_poker.shuffle(deck)

        dealt_cards = []
        for player in self.players:
            pass

