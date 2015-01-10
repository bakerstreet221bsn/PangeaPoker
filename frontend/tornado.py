import traceback
import tornado.web
import tornado.websocket
from messaging.pika_queue import PikaQueueServer
from messaging.message_handler import MessageHandler
from messaging.message_handler import PangeaMessage

example_requests = [
    '{ "message_type": "poll" }',
    '{ "message_type": "dealer_shuffle_cards" , "players": ["8890", "8891"], '
    '"table_id": "1", "dealer_id": "1", "cards": "1"}',
    '{ "message_type": "place_bet" }'
]


class PangeaApplication(tornado.web.Application):
    def __init__(self, port):
        message_queue = PikaQueueServer(port)
        message_queue.start()

        handlers = [
            (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": "./frontend/static"}),
            (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "./frontend/static"}),
            (r"/", MainHandler, dict(port=port)),
            (r"/websocket", WebSocketHandler, dict(message_queue=message_queue))
        ]

        settings = {
            "template_path": "frontend",
        }

        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    port = None

    def initialize(self, port):
        self.port = port

    def get(self):
        requests = "\n\n".join(example_requests)
        self.render("static/index.html", port=self.port, example_requests=requests)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    message_queue = None

    def initialize(self, message_queue):
        self.message_queue = message_queue

    def open(self):
        print("Websocket connection opened")
        pass

    def on_close(self):
        print("Websocket connection closed")
        pass

    def on_message(self, message):
        print("Received message: {0}".format(message))

        try:
            handler = MessageHandler(self.message_queue)
            response = handler.process_message(message)

            self.write_message(response)
        except Exception as ex:
            print("Got exception while trying to process a message from the web socket: %s" % traceback.format_exc())
            response = PangeaMessage.from_exception("", ex)
            self.write_message(response)