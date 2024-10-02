from typing import Callable
from fastapi import FastAPI
from dependency_injector.wiring import inject, Provide
from sqlalchemy import text
from app.core.containers import Container
from app.db.session import session
from app.core.settings.app import AppSettings
from app.core.redis import RedisLock, RedisCache
from asyncio import gather as asyncio_gather


def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings,
) -> Callable:
    @inject
    async def start_app(
        redis_lock: RedisLock = Provide[Container.redis_lock],
        redis_cache: RedisCache = Provide[Container.redis_cache],
    ) -> None:
        # Use a session to verify database connectivity

        await asyncio_gather(
            redis_lock.lock("ping", 1),
            redis_cache.ping(),
            session.execute(text("SELECT 1")),
        )

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        session.close_all()

    return stop_app
