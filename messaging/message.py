import json
from datetime import datetime
import utils

MESSAGE_TYPE_GET_TABLES = "get_tables"
MESSAGE_TYPE_GET_TABLE = "get_table"
MESSAGE_TYPE_PLACE_BET = "place_bet"
MESSAGE_TYPE_POLL = "poll"
MESSAGE_TYPE_JOIN_TABLE = "join_table"
MESSAGE_TYPE_LEAVE_TABLE = "leave_table"
MESSAGE_TYPE_SHUFFLE_CARDS = "shuffle_cards"
MESSAGE_TYPE_UNMASK_CARDS = "unmask_cards"

# Events
MESSAGE_TYPE_PLACED_BET = "placed_bet"
MESSAGE_TYPE_SHUFFLED_CARDS = "shuffled_cards"

class Message(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.created_on = datetime.utcnow()

    def from_json(self, message):
        self.__dict__ = json.load(message)
        print("Parsed json message: " + str(self.__dict__))

    def to_json(self):
        return json.dumps(self.__dict__, default=utils.json_date_handler())