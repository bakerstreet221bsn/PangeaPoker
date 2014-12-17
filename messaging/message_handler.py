from betting import BettingModule
from lobby import LobbyModule
from messaging import PangeaMessage
from messaging.requests import Requests
from messaging.responses import Responses
from utils.errors import PangeaException, PangaeaErrorCodes
from ui import UiModule
from dealer import DealerModule
import traceback


class MessageHandler(object):

    def __init__(self, message_queue):

        self.__message_queue = message_queue
        self.modules = []
        self.modules.append(UiModule())
        self.modules.append(DealerModule(self.__message_queue))

        self.__betting = BettingModule()
        self.__lobby = LobbyModule()

    def process_message(self, json_string):
        # Parse the response from json
        request = PangeaMessage()

        try:
            request.from_json(json_string)
            print("MessageHandler, request message: %s" % request)

            # Each message type should have an associated method
            if request.message_type is None:
                raise PangeaException.missing_field("message_type")
            if not hasattr(self, request.message_type):
                raise PangeaException(PangaeaErrorCodes.InvalidArgument,
                                      "Unknown message type: '%s'" % request.message_type)

            method = getattr(self, request.message_type)

            # Process the request
            response = method(request)

            # Return the response as json
            print("MessageHandler, response message: %s" % response)
            return response.to_json()

        except PangeaException as ex:
            print(traceback.format_exc())
            return PangeaMessage.from_pangea_exception(request.message_type, ex).to_json()
        except Exception as ex:
            print(traceback.format_exc())
            return PangeaMessage.from_exception(request.message_type, ex).to_json()

    ## Supernet requests
    def place_bet(self, request):

        event_req = PangeaMessage(message_type="test")
        self.__message_queue.send_event(event_req)

        response = PangeaMessage()
        return response

    def poll(self, request):
        response = PangeaMessage()

        return response

    ## Mental poker requests
    def dealer_shuffle_cards(self, request):
        if request.players is None:
            raise PangeaException.missing_field("players")
        if request.table_id is None:
            raise PangeaException.missing_field("table_id")
        if request.dealer_id is None:
            raise PangeaException.missing_field("dealer_id")
        if request.cards is None:
            raise PangeaException.missing_field("cards")

        # Each player must shuffle/encrypt the cards
        shuffled_cards = request.cards
        for player_id in request.players:
            print("player_id %s" % player_id)
            queue_request = Requests.shuffle_cards(request.table_id, player_id, shuffled_cards)
            #queue_response = self.__message_queue.send(queue_request)
            queue_response = self.__message_queue.send_rpc(queue_request)
            print("send_rpc response received")
            shuffled_cards = queue_response.cards

        return Responses.dealer_shuffle_cards(request.table_id, request.dealer_id, shuffled_cards)

    def shuffle_cards_req(self, request):
        if request.player_id is None:
            raise PangeaException.missing_field("player_id")

        if request.player_id == self.__message_queue.player_id:
            response = PangeaMessage()
            return response
        else:
            raise PangeaException(PangaeaErrorCodes.InvalidArgument, "This shuffle_cards_resp is for a different player")

    def shuffle_cards_resp(self, request):
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
