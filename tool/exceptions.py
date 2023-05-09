from .log import log


class Exception(Exception):


    def __init__(self, message):
        super().__init__(message)
        log.error(message)
