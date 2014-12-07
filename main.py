from core import PangeaSocketServer, PangeaSocketHandler
from messaging.queue import MessageQueue
import sys

HOST = "localhost"
PORT = 8888

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the port number passed in as a command line parameter instead
        PORT = int(sys.argv[1])

    print("Running socket server on {0}:{1}".format(HOST, PORT))

    server = PangeaSocketServer((HOST, PORT), PangeaSocketHandler)
    server.message_queue = MessageQueue()
    server.message_queue.start()
    server.serve_forever()