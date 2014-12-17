from messaging import PangeaMessage

MESSAGE_TYPES_GET_TABLES = "get_table"


class LobbyMessages(object):

    @staticmethod
    def get_tables_req(self):
        return PangeaMessage(message_type=MESSAGE_TYPES_GET_TABLES)


class LobbyModule(object):

    __lobby_url = "http://api.pangeapoker.com/lobby"

    def __init__(self):
        pass

    def get_tables(self):
        request = LobbyMessages.get_tables_req()
        response = self.__send_request(request)

        return response

    def get_table(self, table_id):
        pass

    def leave_table(self, table_id, player_id):
        pass

    def join_table(self, table_id, player_id):
        pass

    def __send_request(self, request):
        response = PangeaMessage()
        return response