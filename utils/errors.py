from enum import Enum


class PangaeaErrorCodes(Enum):
    NA = 0
    InvalidArgument = 100
    ServerError = 199


class PangeaException(Exception):
    def __init__(self, error_code: PangaeaErrorCodes, error_message):
        super().__init__(error_message)
        self.error_code = error_code

    @staticmethod
    def missing_field(field_name):
        raise PangeaException(PangaeaErrorCodes.InvalidArgument, "Missing field: {0}".format(field_name))