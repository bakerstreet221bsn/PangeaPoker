from messaging.message import *


def place_bet(table_id, player_id, amount):
    return Message(message_type=MESSAGE_TYPE_PLACE_BET, table_id=table_id, player_id=player_id, amount=amount)


def shuffle_cards(table_id, dealer_id, player_id, cards):
    return Message(message_type=MESSAGE_TYPE_SHUFFLE_CARDS, table_id=table_id, dealer_id=dealer_id,
                   player_id=player_id, cards=cards)