from messaging.message import *


def shuffle_cards(table_id, dealer_id, player_id, shuffled_cards):
    return Message(message_type=MESSAGE_TYPE_SHUFFLE_CARDS, table_id=table_id, dealer_id=dealer_id,
                   player_id=player_id, shuffled_cards=shuffled_cards)