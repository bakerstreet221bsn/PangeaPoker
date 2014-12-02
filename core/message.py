import json

MESSAGE_TYPE_GET_TABLES = "GetTables"
MESSAGE_TYPE_BET = "Bet"

MESSAGE_TYPES = [
    MESSAGE_TYPE_GET_TABLES,
    MESSAGE_TYPE_BET
]


def create_bet_message(table, player, amount):
    return Message(dict(messageType=MESSAGE_TYPE_BET, table=table, player=player, amount=amount))


class Message(object):

    def __init__(self, data=None):
        self.data = data

    def from_json(self, message):
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

    def to_json(self):
        if self.data is None:
            print("No data set")
            return None

        if self.get_message_type() is None:
            print("No message type set")
            return None

        msg = {
            "requestType": "poker",
            "args": self.data
        }
        return json.dumps(msg)

    def get_message_type(self):
        if self.data is None:
            return None
        return self.data["messageType"]

