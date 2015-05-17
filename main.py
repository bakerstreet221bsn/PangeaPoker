import sys
import logging

import tornado.ioloop
import tornado.web
import tornado.httpserver

from frontend import PangeaApplication


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#HOST = "localhost"
port = 8888

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the port number passed in as a command line parameter instead
        port = int(sys.argv[1])

    logger.debug("http://localhost:{0}/".format(port))
    logger.debug("http://localhost:{0}/test".format(port))
    logger.debug("Listening with web sockets on port {0}".format(port))

    application = PangeaApplication(port)
    server = tornado.httpserver.HTTPServer(application)

    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()