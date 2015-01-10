from frontend.tornado import PangeaApplication
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver

#HOST = "localhost"
port = 8888

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the port number passed in as a command line parameter instead
        port = int(sys.argv[1])

    print("http://localhost:{0}/".format(port))
    print("Listening with web sockets on port {0}".format(port))

    application = PangeaApplication(port)
    server = tornado.httpserver.HTTPServer(application)

    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()