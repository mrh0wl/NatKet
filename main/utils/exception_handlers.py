from http.client import responses

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .exceptions import (EndpointException, FilterException,
                         LimitException, OffsetException, SlugException,
                         SortException)


async def endpoint_exception_handler(request: Request, exc: EndpointException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status_code': exc.status_code,
            'status_msg': responses[exc.status_code],
            'details': {
                'cause': exc.cause,
                'message': exc.message

            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()[0]
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'status_code': HTTP_422_UNPROCESSABLE_ENTITY,
            'status_msg': 'Validation Error',
            'details': {
                'cause': errors['type'],
                'message': errors['msg'].capitalize()

            }
        },
    )


exception_handlers = {
    FilterException: endpoint_exception_handler,
    LimitException: endpoint_exception_handler,
    OffsetException: endpoint_exception_handler,
    SlugException: endpoint_exception_handler,
    SortException: endpoint_exception_handler,
    RequestValidationError: validation_exception_handler
}
