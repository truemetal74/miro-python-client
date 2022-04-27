class MiroException(Exception):

    def __init__(self, status: int, details: str = ''):
        super(MiroException, self).__init__()
        self.status = status
        self.details = details

    def __str__(self):
        return f'Exception {type(self).__name__} err code = {self.status} extended details: {self.details}'

    # def __init__(self, cause: Exception):
    #     super(MiroException, self).__init__(cause)


class InvalidCredentialsException(MiroException):
    """An authentication error occurred because of bad credentials."""

class APIErrorException(MiroException):
    """API error - e.g. wrong parameters"""

class ObjectNotFoundException(MiroException):
    """The requested object was not found."""


class UnexpectedResponseException(MiroException):
    """The response has an unexpected code or data"""


class InsufficientPermissions(MiroException):
    """Not enough permissions to perform a certain action"""
