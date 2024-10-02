from aiocache.serializers import PickleSerializer
from redis.asyncio import Redis
from aioredlock import Aioredlock, Lock
from app.core.config import get_app_settings


class RedisLock:
    def __init__(self) -> None:
        self.redis_lock = Aioredlock(
            [
                f"{'rediss' if get_app_settings().redis_use_tls else 'redis'}://:@{get_app_settings().redis_url}:{get_app_settings().redis_port}/0"
            ]
        )

    async def lock(self, id: str, lock_timeout=10) -> Lock:
        return await self.redis_lock.lock(id, lock_timeout)

    async def unlock(self, lock: Lock):
        await self.redis_lock.unlock(lock)


class RedisCache:
    def __init__(self) -> None:
        self.redis = Redis(
            host=get_app_settings().redis_url,
            port=get_app_settings().redis_port,
            db=0,
            ssl=get_app_settings().redis_use_tls,
        )
        self._serializer = PickleSerializer()

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        await self.redis.set(key, self._serializer.dumps(value), ex=ttl)

    async def get(self, key: str) -> str:
        return self._serializer.loads(await self.redis.get(key))

    async def ping(self) -> None:
        await self.redis.ping()
