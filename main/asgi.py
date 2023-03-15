import contextlib
import os
import re

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from utils import get_code_samples

# Export Django settings env variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

apps.populate(settings.INSTALLED_APPS)

# This endpoint imports should be placed below the settings env declaration
# Otherwise, django will throw a configure() settings error
from main.api_router import router as api_router
# Get the Django WSGI application we are working with
application = get_wsgi_application()

# This can be done without the function, but making it functional
# tidies the entire code and encourages modularity


def get_application() -> FastAPI:
    # Main Fast API application
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION,
                  description=settings.PROJECT_DESCRIPTION,
                  openapi_url=f"{settings.API_V1_STR}/openapi.json",
                  docs_url=None,
                  redoc_url=None,
                  debug=settings.DEBUG
                  )

    app.mount("/static/js", StaticFiles(directory="static/js"), name="static/js")
    # Set all CORS enabled origins
    app.add_middleware(CORSMiddleware, allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS] or [
                       "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

    @app.get("/docs", include_in_schema=False)
    async def redoc_try_it_out() -> HTMLResponse:
        title = f"{app.title}"
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=title,
            redoc_js_url='/static/js/redoc.standalone.js'
        )

    # Include all api endpoints
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Mounts an independent web URL for Django WSGI application
    app.mount(f"{settings.WSGI_APP_URL}", WSGIMiddleware(application))

    openapi_schema = app.openapi()

    for route in app.routes:
        if route.path.startswith(settings.API_V1_STR) and '.json' not in route.path:
            for method in route.methods:
                path = re.sub(r'{(.*):.*}', r'{\1}', route.path)
                if openapi_schema["paths"].get(path) and method.lower() in openapi_schema["paths"].get(path):
                    code_samples = get_code_samples(route=route, method=method)
                    openapi_schema["paths"][path][method.lower()]["x-codeSamples"] = code_samples

    return app
