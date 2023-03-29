
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.openapi.docs import get_redoc_html
from starlette.responses import HTMLResponse

from main.services import api_router

from .utils import exception_handlers

# This endpoint imports should be placed below the settings env declaration
# Otherwise, django will throw a configure() settings error
# Get the Django WSGI application we are working with
application = get_wsgi_application()

# This can be done without the function, but making it functional
# tidies the entire code and encourages modularity


def get_application() -> FastAPI:

    # Main Fast API application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        exception_handlers=exception_handlers,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=None,
        redoc_url=None,
        contact={
            "name": "API Support",
            "email": "support@natket.com",
            "url": "natket.com"
        },
        debug=settings.DEBUG
    )
    # Set all CORS enabled origins
    allow_origins = [str(origin) for origin in settings.ALLOWED_HOSTS] or ["*"]
    app.add_middleware(CORSMiddleware, allow_origins=allow_origins,
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

    @app.get("/docs", include_in_schema=False)
    async def redoc_try_it_out() -> HTMLResponse:
        title = f"{app.title}"
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=title,
            redoc_js_url='https://cdn.redoc.ly/reference-docs/latest/redocly-reference-docs.min.js'
        )
    # Include all api endpoints
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Mounts an independent web URL for Django WSGI application
    app.mount(f"{settings.WSGI_APP_URL}", WSGIMiddleware(application))

    return app
