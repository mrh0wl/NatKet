from http.client import responses

from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from main.asgi import get_application
from main.exceptions import EndpointException


def custom_openapi():
    # cache the generated schema
    if app.openapi_schema:
        return app.openapi_schema

    # custom settings
    openapi_schema = get_openapi(
        title="NatKet GameAPI",
        version="1.0.0",
        description="NatKet is an API that should help to get game information",
        routes=app.routes,
    )
    # setting new logo to docs
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app = get_application()
app.openapi = custom_openapi


@app.exception_handler(EndpointException)
async def endpoint_exception_handler(request: Request, exc: EndpointException):
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
