

class RequestHandler(object):

    def __init__(self, supernet):
        self.__supernet = supernet

    def process_message(self, message):

        request = Request()
        request.parse(message)

        pass
