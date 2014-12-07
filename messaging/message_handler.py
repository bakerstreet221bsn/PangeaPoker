from messaging import *
from mentalpoker.mental_poker import *
from betting import Betting
from lobby import Lobby
from messaging import PangeaMessage
from messaging.requests import Requests
from messaging.responses import Responses


class MessageHandler(object):

    def __init__(self, message_queue):
        self.__mental_poker = MentalPoker()
        self.__betting = Betting()
        self.__lobby = Lobby()
        self.__message_queue = message_queue

    def process_message(self, json_string):
        # Parse the response from json
        request = PangeaMessage()
        request.from_json(json_string)

        print("Request message: %s" % request)

        # Each message type should have an associated method
        if request.message_type is None:
            raise Exception("Field missing: message_type")
        if not hasattr(self, request.message_type):
            raise Exception("Unknown message type: '%s'" % request.message_type)
        method = getattr(self, request.message_type)

        # Process the request
        response = method(request)
        response.message_type = request.message_type

        # Return the response as json
        print("Response message: %s" % response)
        return response.to_json()

    ## Supernet requests
    def place_bet(self, request):
        response = PangeaMessage()
        return response

    def poll(self, request):
        response = PangeaMessage()

        return response

    ## Mental poker requests
    def dealer_shuffle_cards(self, request):
        if request.players is None:
            raise Exception("Missing field: players")
        if request.table_id is None:
            raise Exception("Missing field: table_id")
        if request.dealer_id is None:
            raise Exception("Missing field: dealer_id")
        if request.cards is None:
            raise Exception("Missing field: cards")

        # Each player must shuffle/encrypt the cards
        shuffled_cards = request.cards
        for player_id in request.players:
            print("player_id %s" % player_id)
            queue_request = Requests.shuffle_cards(request.table_id, player_id, shuffled_cards)
            queue_response = self.__message_queue.send(queue_request)
            shuffled_cards = queue_response.cards


        return Responses.dealer_shuffle_cards(request.table_id, request.dealer_id, shuffled_cards)

    def shuffle_cards(self, request):
        response = PangeaMessage()

        return response

    def unmask_cards(self, request):
        response = PangeaMessage()

        return response

    ## Lobby requests
    def get_table(self, request):
        response = PangeaMessage()

        lobby_response = self.__lobby.get_table(request.table_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message
        else:
            response.table = lobby_response.table

        return response

    def join_table(self, request):
        response = PangeaMessage()
        lobby_response = self.__lobby.leave_table(request.table_id, request.player_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message

        return response

    def leave_table(self, request):
        response = PangeaMessage()
        lobby_response = self.__lobby.leave_table(request.table_id, request.player_id)

        if lobby_response.error_code is not None:
            response.error_code = lobby_response.error_code
            response.error_message = lobby_response.error_message

        return response
