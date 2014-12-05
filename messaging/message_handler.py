from messaging.message import *
from mentalpoker.mental_poker import *
from betting import Betting
from lobby import Lobby


class MessageHandler(object):

    def __init__(self):
        self.__mental_poker = MentalPoker()
        self.__betting = Betting()
        self.__lobby = Lobby()

    def process_message(self, json_string):
        request = Message()
        request.from_json(json_string)

        # Each message type should have an associated method
        method = getattr(self, request.message_type)
        if not method:
            raise Exception("Unknown message type %s" % request.message_type)

        response = method(request)
        return response.to_json()

    ## Supernet requests
    def place_bet(self, request):
        response = Message(message_type=request.message_type)

        return response

    def poll(self, request):
        response = Message(message_type=request.message_type)

        return response

    ## Mental poker requests
    def shuffle_cards(self, request):
        response = Message(message_type=request.message_type)

        return response

    def unmask_cards(self, request):
        response = Message(message_type=request.message_type)

        return response

    ## Lobby requests
    def get_table(self, request):
        response = Message(message_type=request.message_type)

        lobby_response = self.__lobby.get_table(request.table_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message
        else:
            response.table = lobby_response.table

        return response

    def join_table(self, request):
        response = Message(message_type=request.message_type)
        lobby_response = self.__lobby.leave_table(request.table_id, request.player_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message

        return response

    def leave_table(self, request):
        response = Message(message_type=request.message_type)
        lobby_response = self.__lobby.leave_table(request.table_id, request.player_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message

        return response
