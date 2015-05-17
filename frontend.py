import traceback
import tornado.web
import tornado.websocket
from messaging.pika_queue import PikaQueueServer
from messaging.message_handler import MessageHandler
from messaging.message_handler import PangeaMessage
from ui.client import UiClient
from ui.service import UiService
from dealer import DealerClient
import urllib
from datetime import datetime
from tornado.ioloop import PeriodicCallback
from utils.settings import Settings
import logging

example_requests = [
    '{ "message_type": "poll" }',
    '{ "message_type": "dealer_shuffle_cards" , "players": ["8890", "8891"], '
    '"table_id": "1", "dealer_id": "1", "cards": "1"}',
    '{ "message_type": "place_bet" }'
]


class PangeaApplication(tornado.web.Application):
    def __init__(self, port):
        # TODO: Disabling RabbitMQ as we not currently doing P2P
        message_queue = None
        #message_queue = PikaQueueServer(port)
        #message_queue.start()

        settings = Settings()
        frontend_path = settings.get("frontend_path", "../pangea-poker-frontend/client")

        handlers = [
            (r"/test/css/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
            (r"/test/js/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
            (r"/test", MainHandler, dict(port=port)),
            (r"/api/ws", WebSocketHandler, dict(message_queue=message_queue)),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": frontend_path, "default_filename": "index.html"})
        ]

        settings = {
            "template_path": "static",
        }

        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    port = None

    def initialize(self, port):
        self.port = port

    def get(self):
        #requests = "\n\n".join(example_requests)
        requests = ""
        self.render("..\static\index.html", port=self.port, example_requests=requests)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    log = logging.getLogger(__name__)

    POLL_TIME = 5000  # 5 seconds
    polling = False
    poll_callback = None
    last_poll_time = None

    message_queue = None
    dealer_client = None
    ui_client = None
    ui_service = None

    def initialize(self, message_queue):
        self.message_queue = message_queue
        self.dealer_client = DealerClient()
        self.ui_client = UiClient(self.write_message)
        self.ui_service = UiService(self.dealer_client, self.ui_client)

    def check_origin(self, origin):
        parsed_origin = urllib.parse.urlparse(origin)
        return "localhost" in parsed_origin.netloc

    def open(self):
        self.log.debug("Websocket connection opened")

        # Check the table the moment you connect
        self.last_poll_time = datetime.utcnow()
        self.ui_service.table_status(self.last_poll_time)

        self.start_status_poll()

    def on_close(self):
        self.log.debug("Websocket connection closed")
        self.stop_status_poll()
        self.ui_service.leave_table()

    def on_message(self, message):
        print("Received message: {0}".format(message))

        try:
            self.ui_service.handle_message(message)
        except Exception as ex:
            print("Got exception while trying to process a message from the web socket: %s" % traceback.format_exc())
            response = PangeaMessage.from_exception("", ex)
            self.write_message(response.to_json())

    def start_status_poll(self):
        if self.poll_callback:
            self.polling = False
            self.poll_callback.stop()

        self.poll_callback = PeriodicCallback(self.status_poll_elapsed, self.POLL_TIME)
        self.poll_callback.start()
        self.polling = True
        self.last_poll_time = None

    def stop_status_poll(self):
        self.polling = False
        self.last_poll_time = None

        if self.poll_callback:
            self.poll_callback.stop()
            self.poll_callback = None

    def status_poll_elapsed(self):
        if self.polling:
            try:
                self.ui_service.table_status(self.last_poll_time)
            except Exception:
                self.log.debug("Got exception while trying to do a periodic table status check %s"
                               % traceback.format_exc())
            self.last_poll_time = datetime.utcnow()