from messaging import *


class Responses(object):

    @staticmethod
    def dealer_shuffle_cards(table_id, dealer_id, cards):
        return PangeaMessage(message_type=MESSAGE_TYPE_DEALER_SHUFFLE_CARDS, table_id=table_id, dealer_id=dealer_id,
                             shuffled_cards=cards)

    @staticmethod
    def shuffle_cards(table_id, dealer_id, player_id, shuffled_cards):
        return PangeaMessage(message_type=MESSAGE_TYPE_SHUFFLE_CARDS_RESP, table_id=table_id, dealer_id=dealer_id,
                             player_id=player_id, shuffled_cards=shuffled_cards)