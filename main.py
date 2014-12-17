from frontend import PangeaSocketServer, PangeaSocketHandler
from messaging.pika_queue import PikaQueueServer
import sys

global PORT

HOST = "localhost"
PORT = 8888

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the port number passed in as a command line parameter instead
        PORT = int(sys.argv[1])

    print("Running socket server on {0}:{1}".format(HOST, PORT))

    try:
        server = PangeaSocketServer((HOST, PORT), PangeaSocketHandler)
        server.message_queue = PikaQueueServer(PORT)

        server.message_queue.start()
        server.serve_forever()
    except KeyboardInterrupt:
        server.message_queue.shutdown()
        server.shutdown()

#{ "message_type": "dealer_shuffle_cards" , "players": ["8890", "8891"], "table_id": "1", "dealer_id": "1", "cards": "1"}
#{ "message_type": "place_bet" }