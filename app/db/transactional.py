from inspect import iscoroutinefunction
from functools import wraps
from asyncio import gather as async_gather

from starlette.concurrency import run_in_threadpool
from starlette_context import context

# from app.db import session
from app.db.session import session


class Transactional:
    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            context["rollback_fn"] = []
            try:
                result = await func(*args, **kwargs)
                await session.commit()
            except Exception as e:
                await async_gather(
                    *[
                        fn if iscoroutinefunction(fn) else run_in_threadpool(fn)
                        for fn in context["rollback_fn"]
                    ]
                )
                await session.rollback()
                raise e

            return result

        return _transactional
