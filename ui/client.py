import logging
import json

from messaging import PangeaMessage
from utils import PangeaMessageEncoder

logger = logging.getLogger(__name__)


class UiClient(object):
    def __init__(self, write_message_callback):
        self.logger = logging.getLogger(__name__)
        self.write_message_callback = write_message_callback

    def send_message(self, message):
        json_message = message.to_json()
        self.logger.debug("Sending message to frontend: {0}".format(json_message))

        self.write_message_callback(json_message)

    def create_game(self, game_type=None, pot=None, big_blind=None, to_call=None, limit=None, my_turn=None, timer=None):
        game = {}

        self.add_if_not_null(game, "gametype", game_type)
        self.add_if_not_null(game, "pot", pot)
        self.add_if_not_null(game, "bigblind", big_blind)
        self.add_if_not_null(game, "tocall", to_call)
        self.add_if_not_null(game, "limit", limit)
        self.add_if_not_null(game, "myturn", my_turn)
        self.add_if_not_null(game, "timer", timer)

        return game

    def create_deal(self, dealer=None, hole_cards=None, board_cards=None):
        deal = {}

        self.add_if_not_null(deal, "dealer", dealer)
        self.add_if_not_null(deal, "holecards", hole_cards)
        self.add_if_not_null(deal, "board", board_cards)

        return deal

    def create_chat(self, chat_message):
        return chat_message

    def create_player(self, sitting=None, stack=None, seat_number=None, hole_cards=None):
        player = {}

        self.add_if_not_null(player, "sitting", sitting)
        self.add_if_not_null(player, "stack", stack)
        self.add_if_not_null(player, "seat", seat_number)
        self.add_if_not_null(player, "holecards", hole_cards)

        return player

    def create_chips_to_pot(self):
        message = {}
        message["action"] = {"chipsToPot": 0}
        return message

    def create_chips_to_player(self, seat_number):
        message = {}
        message["action"] = {"chipsToPlayer": seat_number}
        return message

    def create_return_player_cards(self, seat_number):
        message = {}
        message["action"] = {"returnPlayerCards": seat_number}
        return message

    def create_error(self, exception):
        message = {}
        message["error"] = str(exception)
        return message

    def create_seat(self, seat_number=None, stack=None, action=None, playing=None, player=None,
                    empty=None, player_cards=None, bet=None, name=None, status=None):
        seat = {}
        self.add_if_not_null(seat, "seat", seat_number)
        self.add_if_not_null(seat, "stack", stack)
        self.add_if_not_null(seat, "action", action)
        self.add_if_not_null(seat, "playing", playing)
        self.add_if_not_null(seat, "player", player)
        self.add_if_not_null(seat, "empty", empty)
        self.add_if_not_null(seat, "playercards", player_cards)
        self.add_if_not_null(seat, "bet", bet)
        self.add_if_not_null(seat, "name", name)
        self.add_if_not_null(seat, "action", status)

        return seat

    def add_if_not_null(self, dictionary, name, value):
        if value is not None:
            dictionary[name] = value


