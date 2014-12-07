import socketserver
import traceback
from messaging import message_handler


class PangeaSocketServer(socketserver.ThreadingTCPServer):
    message_queue = None


class PangeaSocketHandler(socketserver.BaseRequestHandler):

    def handle(self):
        message_queue = self.server.message_queue

        try:
            print("Received request from %s" % str(self.client_address))

            # Read message from client
            msg = ""
            while True:
                data = self.request.recv(1024)
                if not data:
                    break

                print("Received data %s" % data)
                msg += data.decode("utf-8")

                # Assuming (for the moment) that a newline indicates the end of message
                if msg.endswith("\n"):
                    break

            # Process message
            handler = message_handler.MessageHandler(message_queue)
            response = handler.process_message(msg)

            # Send response back to client
            self.request.sendall(response.encode("utf-8"))
        except Exception:
            # TODO: Should probably return some kind of error response if we fail to parse the message

            print("Got exception while trying to read from the client connection: %s" % traceback.format_exc())