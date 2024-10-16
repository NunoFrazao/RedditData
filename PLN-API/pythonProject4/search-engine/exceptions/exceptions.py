from types import TracebackType


class IllegalValueException(Exception):
    pass

class EmptyValueException(Exception):
    pass

class NotDataFoundException(Exception):
    pass

class InsufficientDataException(Exception):
    pass

class RequestRedditException(Exception):
    pass

