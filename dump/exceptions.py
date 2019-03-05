class DumpException(Exception):
    pass


class MissingAuthorization(DumpException):
    pass


class InvalidChunkSize(DumpException):
    pass
