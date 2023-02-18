import os
from http.client import responses

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

# Export Django settings env variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

apps.populate(settings.INSTALLED_APPS)

# This endpoint imports should be placed below the settings env declaration
# Otherwise, django will throw a configure() settings error
from main.api_router import router as api_router
from main.exceptions import LimitException

# Get the Django WSGI application we are working with
application = get_wsgi_application()

# This can be done without the function, but making it functional
# tidies the entire code and encourages modularity


def get_application() -> FastAPI:
    # Main Fast API application
    app = FastAPI(title=settings.PROJECT_NAME,
                  openapi_url=f"{settings.API_V1_STR}/openapi.json", debug=settings.DEBUG)

    # Set all CORS enabled origins
    app.add_middleware(CORSMiddleware, allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS] or [
                       "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

    # Include all api endpoints
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Mounts an independent web URL for Django WSGI application
    app.mount(f"{settings.WSGI_APP_URL}", WSGIMiddleware(application))

    return app


app = get_application()

@app.exception_handler(LimitException)
async def limit_exception_handler(request: Request, exc: LimitException):
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
