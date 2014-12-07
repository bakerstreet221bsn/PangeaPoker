from threading import Thread
from messaging import PangeaMessage
from messaging.message_handler import MessageHandler
import amqpy

QUEUE_NAME = "pangea"
EXCHANGE_NAME = "pangea"


class MessageConsumer(amqpy.AbstractConsumer):
    def run(self, msg: amqpy.Message):
        print("Received message from queue: {}".format(msg.body))
        msg.ack()


class MessageQueue(Thread):

    server = None
    client = None

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.receive()

    def receive(self):
        print("Started message queue")

        conn = amqpy.Connection()
        ch = conn.channel()

        ch.exchange_declare(EXCHANGE_NAME, "direct")
        ch.queue_declare(QUEUE_NAME)
        ch.queue_bind(QUEUE_NAME, exchange=EXCHANGE_NAME)

        consumer = MessageConsumer(ch, QUEUE_NAME)
        consumer.declare()

        while True:
            conn.drain_events(timeout=None)

    def send(self, request):
        msg = request.to_json()
        print("Sending message to queue %s" % msg)

        conn = amqpy.Connection()
        ch = conn.channel()

        ch.exchange_declare(EXCHANGE_NAME, "direct")
        ch.queue_declare(QUEUE_NAME)
        ch.queue_bind(QUEUE_NAME, exchange=EXCHANGE_NAME)

        ch.basic_publish(amqpy.Message(msg), exchange=EXCHANGE_NAME)

        #rsp = ch.basic_get(QUEUE_NAME)
        #print("Rsp: {}".format(rsp))
        #rsp.ack()

        return PangeaMessage()

