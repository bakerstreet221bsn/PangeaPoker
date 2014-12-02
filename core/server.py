import socket
import sys
from threading import Thread


class Server(object):

    def start(self, port):
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

    def client_thread(self, connection):
        connection.send("CONNECTED!\n")

        while True:
            data = connection.recv(1024)
            if not data:
                break

            reply = "RECEIVED: " + data
            connection.sendall(reply)

        connection.close()


