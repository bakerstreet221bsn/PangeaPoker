import socket
import sys
import traceback
from threading import Thread
from messaging import message_handler


def start(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(("", port))
    except socket.error as msg:
        print("Bind failed. Error code: " + str(msg[0]) + ', Message: ' + msg[1])
        sys.exit()

    s.listen(10)

    print("Listening")

    while 1:
        connection, address = s.accept()
        print("Connected with: " + address[0] + ":" + str(address[1]))

        thread = Thread(target=client_thread, args=connection)
        thread.start()

    s.close()


def client_thread(connection):

    try:
        # Read message from client
        message = ""
        while True:
            data = connection.recv(1024)
            if not data:
                break

            message += message
            print("Received data: " + data)

        # Process message
        handler = message_handler.MessageHandler()
        response = handler.process_message(message)

        # Send response back to client
        connection.replyall(response)
    except Exception:
        print("Got exception while trying to read from the client connection" + traceback.format_exc())
    finally:
        try:
            connection.close()
        except Exception as ex:
            print("Exception received while trying to close the client connection " + ex)