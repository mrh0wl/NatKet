import re
from http.client import responses

from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from main.asgi import get_application, settings
from main.exceptions import EndpointException

from utils import get_code_samples


def custom_openapi():
    # cache the generated schema
    if app.openapi_schema:
        return app.openapi_schema

    # custom settings
    openapi_schema = get_openapi(
        title="NatKet Video Games Database API",
        version="1.0.0",
        description="One of the principles behind NatKet.com is accessibility of data. We wish to share the data with anyone who wants to build cool video game oriented websites, apps and services.\n\
            \nThis means that you are not only contributing to the value of NatKet but to thousands of other projects as well. We are looking forward to see what exciting game related projects you come up with. Happy coding!\n\
            \nFor a high level overview of our juicy data, check out the endpoints section.",
        routes=app.routes,
    )

    for route in app.routes:
        if route.path.startswith(settings.API_V1_STR) and '.json' not in route.path:
            for method in route.methods:
                path = re.sub(r'{(.*):.*}', r'{\1}', route.path)
                if openapi_schema["paths"].get(path) and method.lower() in openapi_schema["paths"].get(path):
                    code_samples = get_code_samples(route=route, method=method)
                    openapi_schema["paths"][path][method.lower()]["x-codeSamples"] = code_samples

    # setting new logo to docs
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app = get_application()
# app.openapi = custom_openapi


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
