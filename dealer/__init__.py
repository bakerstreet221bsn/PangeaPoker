import traceback
import json
import logging
import time
import datetime
import calendar

from wsgiref.handlers import format_date_time
from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError
from utils.errors import PangeaException, PangaeaErrorCodes
from messaging import PangeaMessage
from utils.settings import Settings


class DealerClient(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        settings = Settings()
        self.base_url = settings.get("dealer_url", "http://localhost:10006/api/")

    # -- Player --
    def create_player(self, username):
        body = PangeaMessage(username=username)
        return self.send_request("players", "POST", body)

    def get_player(self, player_id):
        return self.send_request("players/{0}".format(player_id), "GET")

    def player_exists(self, player_id):
        return self.send_request("player/exists?player_id={0}".format(player_id), "GET")

    def join_table(self, table_id, player_id, seat_number, stack):
        body = PangeaMessage(table_id=table_id, player_id=player_id, seat_number=seat_number, stack=stack)
        return self.send_request("seats", "POST", body)

    def leave_table(self, table_id, player_id):
        return self.send_request("seats?table_id={0}&player_id={1}".format(table_id, player_id), "DELETE")

    # -- Lobby --
    def create_lobby(self, name):
        body = PangeaMessage(name=name)
        return self.send_request("lobbies", "POST", body)

    def get_lobbies(self):
        return self.send_request("lobbies", "GET")

    def get_lobby(self, lobby_id):
        return self.send_request("lobbies/{0}".format(lobby_id), "GET")

    # -- Table --
    def create_table(self, lobby_id, name):
        body = PangeaMessage(lobby_id=lobby_id, name=name)
        return self.send_request("tables", "POST", body)

    def get_default_table(self):
        body = PangeaMessage(use_default=True)
        return self.send_request("tables", "POST", body)

    def delete_table(self, table_id):
        return self.send_request("tables?table_id={0}".format(table_id), "DELETE")

    def delete_default_table(self):
        return self.send_request("tables?default=true", "DELETE")

    def get_tables(self, lobby_id=None):
        endpoint = "tables"
        if lobby_id:
            endpoint += "?lobby_id={0}".format(lobby_id)

        return self.send_request(endpoint, "GET")

    def get_table(self, table_id, player_id=None):
        endpoint = "tables/{0}".format(table_id)
        if player_id:
            endpoint += "?player_id={0}".format(player_id)

        return self.send_request(endpoint, "GET")

    def get_table_status(self, table_id, player_id=None, last_check=None, log_messages=False):
        endpoint = "tables/status/{0}".format(table_id)

        if player_id:
            endpoint += "?player_id={0}".format(player_id)

        return self.send_request(endpoint, "GET", if_modified_since=last_check, log_messages=log_messages)

    # -- Bet --
    def bet(self, table_id, player_id, amount):
        body = PangeaMessage(table_id=table_id, player_id=player_id, amount=amount)
        return self.send_request("bets", "POST", body)

    def check(self, table_id, player_id):
        body = PangeaMessage(table_id=table_id, player_id=player_id, check=True)
        return self.send_request("bets", "POST", body)

    def fold(self, table_id, player_id):
        body = PangeaMessage(table_id=table_id, player_id=player_id, fold=True)
        return self.send_request("bets", "POST", body)

    # -- Chat --
    def create_chat(self, table_id, player_id, chat_message):
        body = PangeaMessage(table_id=table_id, player_id=player_id, chat_message=chat_message)
        return self.send_request("chats", "POST", body)

    def send_request(self, endpoint, method, body=None, if_modified_since=None, log_messages=True):
        url = self.base_url + endpoint
        headers = {"Content-Type": "application/json"}

        if if_modified_since and isinstance(if_modified_since, datetime.datetime):
            stamp = calendar.timegm(if_modified_since.timetuple())
            headers["If-Modified-Since"] = format_date_time(stamp)

        request = HTTPRequest(url=url, method=method, headers=headers)
        if body is not None:
            request.body = body.to_json()

        client = HTTPClient()
        response = PangeaMessage()

        if log_messages:
            self.logger.info("Sending request, Url: {0}, Method: {1}, Body: {2}"
                             .format(request.url, request.method, request.body))

        try:
            http_response = client.fetch(request)

            if http_response.body:
                if log_messages:
                    self.logger.info("Received response: {0}".format(http_response.body))

                response.from_json(http_response.body)

        except HTTPError as e:
            # HTTPError is raised for non-200 responses
            self.logger.error("Exception while sending request: {0}".format(traceback.format_exc()))

            if e.response and e.response.body:
                self.logger.debug("Received error response: {0}".format(e.response.body))
                error = PangeaMessage().from_json(e.response.body)
                raise PangeaException(error.error_code, error.error_message)
            else:
                raise PangeaException(PangaeaErrorCodes.ServerError, "Error sending request")
        except Exception:
            self.logger.error("Exception while sending request: {0}".format(traceback.format_exc()))
            raise PangeaException(PangaeaErrorCodes.ServerError, "Error sending request")
        finally:
            client.close()
        return response


class DealerEvents(object):
    PLAYER_JOIN_TABLE = "player_join"
    PLAYER_LEAVE_TABLE = "player_leave"
    PLAYER_BET = "player_bet"
    PLAYER_CHECK = "player_check"
    PLAYER_FOLD = "player_fold"
    PLAYER_CALL = "player_call"
    PLAYER_RAISE = "player_call"
    HAND_COMPLETE = "hand_complete"
    HAND_DEAL = "hand_deal"


class PangaeaDealerErrorCodes():
    NA = 0
    InvalidArgumentError = 200
    NotFoundError = 201
    AlreadyExists = 202
    BettingError = 203
    ServerError = 299