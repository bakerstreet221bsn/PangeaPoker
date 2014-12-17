from messaging import PangeaMessage
from core import PangeaModule

DEALER_MESSAGE_TYPE_JOIN_TABLE_REQ = "dealer_join_table_req"


class DealerModule(PangeaModule):

    def __init__(self, message_queue):
        self.__message_queue = message_queue

    def join_table(self, table_id, player_id):
        request = DealerMessages.join_table_req(table_id, player_id)
        response = self.__send_request(request)
        return response

    def leave_table(self, table_id, player_id):
        pass

    def place_bet(self, table_id, player_id):
        pass

    def fold_hand(self, table_id, player_id):
        pass

    def __send_request(self, request):
        response = PangeaMessage()
        return response


class DealerMessages(object):

    @staticmethod
    def join_table_req(table_id, player_id):
        return PangeaMessage(message_type=DEALER_MESSAGE_TYPE_JOIN_TABLE_REQ, table_id=table_id, player_id=player_id)