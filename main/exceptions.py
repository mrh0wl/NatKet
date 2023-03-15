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

    def to_dict(self):
        return self.__dict__


class LimitException(EndpointException):
    limit_errors = {
        0: (400, 'Limit too low', 'Limit parameter should be a positive integer'),
        1: (400, 'Limit too low', 'Limit parameter should be greater than zero'),
        2: (403, 'Request limit too high', 'The maximum limit allowed is 20'),
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


class OffsetException(EndpointException):
    def __init__(self):
        status_code, cause, message = (400, 'Offset too low', 'Offset can\'t be lower than zero.')
        super().__init__(status_code=status_code, cause=cause, message=message)


class SlugException(EndpointException):
    def __init__(self):
        status_code, cause, message = (404, 'Game not found', 'Slug input not found in database.')
        super().__init__(status_code=status_code, cause=cause, message=message)


class FilterException(EndpointException):
    def __init__(self, code: int = 1, key: str = '', model: str = ''):
        type_errors = {
            0: (400, 'Attribute not found', f'No attribute \'{key}\' in \'{model}\' schema.'),
            1: (400, 'Invalid filter key', 'Filter key must be specified.'),
            2: (400, 'Invalid filter key', 'Filter key can only be a single word.')
        }
        status_code, cause, message = type_errors[code]
        super().__init__(status_code=status_code, cause=cause, message=message)


class SortException(EndpointException):
    def __init__(self, *args, **kwargs):
        status_code, cause, message = (404, 'Field not found', f'Field input not found in: ({", ".join(self.args)}).'.strip())
        super(EndpointException, self).__init__(status_code=status_code, cause=cause, message=message)
