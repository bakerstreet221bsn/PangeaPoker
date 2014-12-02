from core.message import Message

class MessageHandler(object):

    def __init__(self):
        pass

    def process_message(self, message):
        req = Message()
        req.parse(message)
