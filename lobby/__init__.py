from lobby import requests
from messaging.message import *
from datetime import datetime

class Lobby(object):

    __lobby_url = "http://api.pangeapoker.com/lobby"

    def __init__(self):
        pass

    def get_tables(self):
        request = requests.get_tables()
        response = self.__send_request(request)

        return response

    def get_table(self, table_id):
        pass

    def leave_table(self, table_id, player_id):
        pass

    def join_table(self, table_id, player_id):
        pass

    def __send_request(self, request):
        return Message()