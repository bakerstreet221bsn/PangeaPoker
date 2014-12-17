import json
from datetime import datetime
import utils
from utils.errors import PangeaException, PangaeaErrorCodes

MESSAGE_TYPE_GET_TABLES = "get_tables"
MESSAGE_TYPE_GET_TABLE = "get_table"
MESSAGE_TYPE_PLACE_BET = "place_bet"
MESSAGE_TYPE_POLL = "poll"
MESSAGE_TYPE_JOIN_TABLE = "join_table"
MESSAGE_TYPE_LEAVE_TABLE = "leave_table"
MESSAGE_TYPE_SHUFFLE_CARDS_REQ = "shuffle_cards_req"
MESSAGE_TYPE_SHUFFLE_CARDS_RESP = "shuffle_cards_resp"
MESSAGE_TYPE_UNMASK_CARDS = "unmask_cards"
MESSAGE_TYPE_DEALER_SHUFFLE_CARDS = "dealer_shuffle_cards"

# Events
MESSAGE_TYPE_PLACED_BET = "placed_bet"
MESSAGE_TYPE_SHUFFLED_CARDS = "shuffled_cards"


class PangeaMessage(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.created_on = datetime.utcnow()

    def from_json(self, msg):
        self.__dict__ = json.loads(msg)

    def to_json(self):
        return json.dumps(self.__dict__, default=utils.json_date_handler)

    def __str__(self):
        return self.to_json()

    def __getattr__(self, item):
        # Return None rather then throwing an AttributeError exception
        return None

    @staticmethod
    def from_pangea_exception(message_type, ex: PangeaException):
        return PangeaMessage(message_type=str(message_type),
                             error_code=ex.error_code.value,
                             error_message=str(ex.args))

    @staticmethod
    def from_exception(message_type, ex: Exception):
        return PangeaMessage(message_type=str(message_type),
                             error_code=PangaeaErrorCodes.ServerError.value,
                             error_message=str(ex.args))

    @staticmethod
    def create_empty_message(message_type):
        return PangeaMessage(message_type=message_type)