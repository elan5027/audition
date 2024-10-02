from fastapi import Path, Depends
from starlette_context import context
from dependency_injector.wiring import Provide, inject

from app.core.containers import Container
from app.api.errors.http_error import (
    UnauthorizedException,
    PermissionDeniedException,
)
