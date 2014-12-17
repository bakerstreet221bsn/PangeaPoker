from threading import Thread
from messaging import PangeaMessage
from messaging.message_handler import MessageHandler
from messaging import *
#import amqpy

QUEUE_NAME = "pangeapoker"
EVENT_QUEUE_NAME = "pangeapoker"
EXCHANGE_NAME = "pangeapoker"


class MessageConsumer(amqpy.AbstractConsumer):

    player_id = None

    def run(self, msg: amqpy.Message):
        print("Received message from queue: {}".format(msg.body))

        message = PangeaMessage()
        message.from_json(msg.body)

        print(self.player_id)
        print(message.player_id)

        if message.message_type == MESSAGE_TYPE_SHUFFLE_CARDS:
            if str(message.player_id) == str(self.player_id):
                print("Got shuffle card message and its player_id matches")
                msg.ack()
            else:
                print("Got shuffle card message and but its player_id does not match")
                msg.reject(requeue=False)
        else:
            msg.ack()


class MessageQueue(Thread):

    player_id = None

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.receive()

    def receive(self):
        print("Started message queue")

        conn = amqpy.Connection()
        ch = conn.channel()

        ch.exchange_declare(EXCHANGE_NAME, "fanout")
        ch.queue_declare(EVENT_QUEUE_NAME)
        ch.queue_bind(EVENT_QUEUE_NAME, exchange=EXCHANGE_NAME)

        consumer = MessageConsumer(ch, EVENT_QUEUE_NAME)
        consumer.player_id = self.player_id

        consumer.declare()

        while True:
            conn.drain_events(timeout=None)

    def send(self, request):
        msg = request.to_json()
        print("Sending message to queue %s" % msg)

        conn = amqpy.Connection()
        ch = conn.channel()
        ch.mode=amqpy.Channel.CH_MODE_CONFIRM

        ch.exchange_declare(EXCHANGE_NAME, "fanout")
        ch.queue_declare(QUEUE_NAME)
        ch.queue_bind(QUEUE_NAME, exchange=EXCHANGE_NAME)
        ch.basic_publish_confirm(amqpy.Message(msg), exchange=EXCHANGE_NAME, mandatory=True)

        rsp = ch.basic_get(QUEUE_NAME)
        print("Rsp: {}".format(rsp.body))
        rsp.ack()

        return PangeaMessage()

    def send_event(self, request):
        msg = request.to_json()
        print("Sending event message to queue %s" % msg)

        conn = amqpy.Connection()
        ch = conn.channel()

        ch.exchange_declare(EXCHANGE_NAME, "fanout")
        ch.queue_declare(EVENT_QUEUE_NAME)
        ch.queue_bind(EVENT_QUEUE_NAME, exchange=EXCHANGE_NAME)
        ch.basic_publish(amqpy.Message(msg), exchange=EXCHANGE_NAME)

        return PangeaMessage()

