from messaging import *


def get_tables():
    return PangeaMessage(message_type=MESSAGE_TYPE_GET_TABLES)


def get_table(table_id):
    return PangeaMessage(message_type=MESSAGE_TYPE_GET_TABLE, table_id=table_id)


def join_table(table_id, player_id):
    return PangeaMessage(message_type=MESSAGE_TYPE_JOIN_TABLE, table_id=table_id, player_id=player_id)