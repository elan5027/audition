from fastapi import FastAPI
from app.core.sqlalchemy import SQLAlchemyMiddleware
from app.core.config import get_app_settings
from app.core import logger
from app.core.app_events import create_start_app_handler, create_stop_app_handler
from app.api.route import router as api_router
from app.core.containers import Container
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette_context.middleware import ContextMiddleware
from app.api.errors.http_error import (
    APIAuthException,
    APIException,
    ForbiddenException,
    auth_error_handler,
    forbidden_error_handler,
    api_error_handler,
)


def get_application() -> FastAPI:
    origins = ["http://localhost", "https://localhost", "https://www.kpopmentor.com"]

    settings = get_app_settings()
    logger.init(settings)

    application = FastAPI(**settings.fastapi_kwargs)
    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    container = Container()
    container.config.from_dict(settings.model_dump())

    application.include_router(api_router)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
        allow_headers=[
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
        ],
    )
    application.add_middleware(SQLAlchemyMiddleware)
    application.add_middleware(ContextMiddleware)
    application.add_exception_handler(Exception, api_error_handler)
    application.add_exception_handler(APIException, api_error_handler)
    application.add_exception_handler(APIAuthException, auth_error_handler)
    application.add_exception_handler(ForbiddenException, forbidden_error_handler)

    return application


app = get_application()


@app.get("/healthcheck")
async def healthcheck():
    return "OK"
