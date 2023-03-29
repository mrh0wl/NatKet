import re

from fastapi.openapi.utils import get_openapi

from main.asgi import get_application, settings
from utils import get_code_samples


def custom_openapi():
    # cache the generated schema
    if app.openapi_schema:
        return app.openapi_schema

    # custom settings
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        tags=[
            {
                "name": "Endpoints",
                "description": "API Endpoints"
            }
        ],
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    openapi_schema['x-tagGroups'] = [
        {
            "name": "Endpoints",
            "tags": [
                "Games",
                "Player Perspectives",
                "Genres",
                "Keywords",
                "Themes",
                "Platforms",
                "Languages"
            ]
        }
    ]
    app.openapi_schema = openapi_schema

    for route in app.routes:
        if route.path.startswith(settings.API_V1_STR) and '.json' not in route.path:
            for method in route.methods:
                path = re.sub(r'{(.*):.*}', r'{\1}', route.path)
                if openapi_schema["paths"].get(path) and method.lower() in openapi_schema["paths"].get(path):
                    code_samples = get_code_samples(route=route, method=method)
                    openapi_schema["paths"][path][method.lower()]["x-codeSamples"] = code_samples

    return app.openapi_schema


app = get_application()
app.openapi = custom_openapi
