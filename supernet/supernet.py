import json


class Supernet(object):

    def __init__(self):
        pass

    def send_bet_message(self, table, player, amount):

        args = {
            "table": table,
            "player": player,
            "amount": amount
        }

        request = self.__create_message(args)
        response = self.__parse_message(self.__send_message(request))
        return response

    # Private functions
    def __create_message(self, args):
        return json.dumps({
            "requestType": "poker",
            "args": args
        })

    def __parse_message(self, message):
        parsed = json.load(message)
        return parsed["args"]

    def __send_message(self, message):
        return ""