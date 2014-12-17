from utils.errors import PangeaException, PangaeaErrorCodes
from messaging import PangeaMessage


class PangeaModule(object):

    def process_message(self, request: PangeaMessage):
        if request is None:
            raise PangeaException(PangaeaErrorCodes.InvalidArgument, "request is not set")
        if request.message_type is None:
            raise PangeaException.missing_field("message_type")
        if not hasattr(self, request.message_type):
            raise PangeaException(PangaeaErrorCodes.InvalidArgument,
                                  "Unknown message type: '%s'" % request.message_type)

        method = getattr(self, request.message_type)
        return method(request)

    def can_process_message(self, request: PangeaMessage):
        if request is None or request.message_type is None:
            return False
        return hasattr(self, request.message_type)


