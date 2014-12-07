from messaging import *


class Requests(object):

    @staticmethod
    def place_bet(table_id, player_id, amount):
        return PangeaMessage(message_type=MESSAGE_TYPE_PLACE_BET, table_id=table_id, player_id=player_id, amount=amount)

    @staticmethod
    def dealer_shuffle_cards(table_id, dealer_id, players, cards):
        return PangeaMessage(message_type=MESSAGE_TYPE_DEALER_SHUFFLE_CARDS, table_id=table_id, dealer_id=dealer_id,
                             players=players, cards=cards)

    @staticmethod
    def shuffle_cards(table_id, player_id, cards):
        return PangeaMessage(message_type=MESSAGE_TYPE_SHUFFLE_CARDS, table_id=table_id, player_id=player_id, cards=cards)