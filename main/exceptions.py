from typing import Any, Dict, Union


class EndpointException(Exception):
    def __init__(self,
                 status_code: int,
                 cause: str,
                 message: Union[str, Dict[str, Any]]
                 ):
        self.status_code = status_code
        self.cause = cause
        self.message = message

        super(EndpointException, self).__init__(message)


class LimitException(EndpointException):
    limit_errors = {
        0: (400, 'Limit too low', 'Limit parameter should be a positive integer.'),
        1: (400, 'Limit too low', 'Limit parameter should be greater than 0.'),
        2: (403, 'Request limit too high', 'The maximum limit allowed is 20.'),
    }

    def __init__(self, limit: int):
        status_code, cause, message = self.limit_errors.get(
            self._get_error_type(limit),
            (500, 'Unknown error', 'An unknown error occurred. Try again later.')
        )

        super().__init__(status_code=status_code, cause=cause, message=message)

    def _get_error_type(self, limit: int) -> int:
        if limit < 1:
            return 1
        elif limit < 0:
            return 0
        elif limit > 20:
            return 2
        else:
            return -1

    def to_dict(self):
        return self.__dict__


class SlugException(EndpointException):
    def __init__(self):
        status_code, cause, message = (400, 'Game not found', 'Slug input not found in database')
        super().__init__(status_code=status_code, cause=cause, message=message)
