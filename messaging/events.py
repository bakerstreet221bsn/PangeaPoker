from messaging import *


def placed_bet(table_id, player_id, amount):
    return PangeaMessage(message_type=MESSAGE_TYPE_PLACED_BET, table_id=table_id, player_id=player_id, amount=amount)