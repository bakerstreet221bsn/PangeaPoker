from threading import Thread
import pika
import uuid
import time
from messaging import PangeaMessage
from messaging import message_handler
import logging
from utils.errors import PangeaException, PangaeaErrorCodes

EVENTS_EXCHANGE_NAME = "pangeapoker"
RPC_EXCHANGE_NAME = "pangeapoker_rpc"


def create_client_routing_key(client_id):
    return "clients.{0}".format(str(client_id))


class PikaQueueClient(object):

    response = None
    correlation_id = None

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        print("PikaQueueClient, on_response, ch: {0}, method: {1}, props: {2}, body: {3}"
              .format(ch, method, props, body))

        if self.correlation_id == props.correlation_id:
            print("Matching response for this client correlation_id found")
            self.response = body

    def send(self, message):
        if message is None:
            raise PangeaException(PangaeaErrorCodes.ServerError, "message is null")
        if message.player_id is None:
            raise PangeaException(PangaeaErrorCodes.InvalidArgument,
                                  "Cannot send message to client without a player_id to identify it")

        self.response = None
        self.correlation_id = str(uuid.uuid4())

        json_msg = message.to_json()
        routing_key = create_client_routing_key(message.player_id)

        properties = pika.BasicProperties(reply_to=self.callback_queue,
                                          correlation_id=self.correlation_id,
                                          content_type="application/json")

        print("Sending rpc message to queue {0}, using correlation_id: {1}".format(json_msg, self.correlation_id))
        self.channel.basic_publish(exchange="", routing_key=routing_key, properties=properties, body=json_msg)

        while self.response is None:
            self.connection.process_data_events()
            self.connection.sleep(0.1)

        print("Received message from queue %s" % self.response)
        response_msg = PangeaMessage()
        response_msg.from_json(self.response.decode("utf-8"))
        return response_msg

    def close(self):
        print("Stopping client")
        if not (self.connection.is_closed or self.connection.is_closing):
            self.connection.close()


class PikaQueueServer(Thread):

    def __init__(self, player_id):
        super().__init__()

        self.client = None
        self.player_id = player_id
        self.message_handler = message_handler.MessageHandler(self)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

        # Broadcast messages
        self.channel.exchange_declare(exchange=EVENTS_EXCHANGE_NAME, type="fanout")
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=EVENTS_EXCHANGE_NAME, queue=queue_name)
        self.channel.basic_consume(self.on_event_request, queue=queue_name)

        # Peer to peer messages
        routing_key = create_client_routing_key(self.player_id)

        self.channel.queue_declare(queue=routing_key)
        self.channel.basic_consume(self.on_rpc_request, queue=routing_key)

    def run(self):
        self.start_listening()

    def start_listening(self):
        print("Message queue started")
        self.channel.start_consuming()

    def shutdown(self):
        print("Message queue stopped")
        self.channel.stop_consuming()
        self.connection.close()

        if self.client is not None:
            self.client.close()

    def on_rpc_request(self, ch, method, props, body):
        print("PikaQueueServer, on_rpc_request, ch: {0}, method: {1}, props: {2}, body: {3}"
              .format(ch, method, props, body))

        response = self.message_handler.process_message(body.decode("utf-8"))

        properties = pika.BasicProperties(correlation_id=props.correlation_id, content_type="application/json")
        self.channel.basic_publish(exchange="", routing_key=str(props.reply_to),
                                   properties=properties, body=response)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def on_event_request(self, ch, method, props, body):
        print("PikaQueueServer, on_event_request, ch: {0}, method: {1}, props: {2}, body: {3}"
              .format(ch, method, props, body))

        response = self.message_handler.process_message(body.decode("utf-8"))

        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def send_event(self, message):
        json_msg = message.to_json()
        print("Send event message to queue: {0}".format(json_msg))
        properties = pika.BasicProperties(content_type="application/json")
        self.channel.basic_publish(exchange=EVENTS_EXCHANGE_NAME, routing_key="", properties=properties, body=json_msg)

    def send_rpc(self, message):
        if self.client is None:
            self.client = PikaQueueClient()

        return self.client.send(message)