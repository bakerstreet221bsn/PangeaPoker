import json

MESSAGE_TYPE_GET_TABLES = "GetTables"
MESSAGE_TYPE_BET = "Bet"

MESSAGE_TYPES = [
    MESSAGE_TYPE_GET_TABLES,
    MESSAGE_TYPE_BET
]


class Request(object):

    data = None

    def __init__(self):
        pass

    def parse(self, message):
        parsed = json.load(message)
        print(parsed)

        if parsed["requestType"] != "poker":
            print("Expecting request type 'poker'")
            return False

        if parsed["args"] is None:
            print("Missing args")
            return False

        message_type = parsed["args"]["messageType"]
        if message_type is None:
            print("Missing message type")
            return False

        if message_type not in MESSAGE_TYPES:
            print("Unexpected message type")
            return False

        self.data = parsed["args"]
        return True

    def get_message_type(self):
        if self.data is None:
            return None
        return self.data["messageType"]

