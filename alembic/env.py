# alembic/env.py
import sys
import os

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.realpath(__file__))

# 프로젝트 루트 디렉토리 경로 (alembic 디렉토리의 상위 디렉토리)
project_root = os.path.abspath(os.path.join(current_dir, ".."))

# sys.path에 프로젝트 루트 디렉토리 추가
sys.path.append(project_root)
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config 객체를 가져옵니다.
config = context.config

# 로그 설정을 가져옵니다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모델을 임포트합니다.
from app.models.base import Base  # Base는 모든 모델의 메타데이터를 포함합니다.

target_metadata = Base.metadata

# 데이터베이스 URL을 가져옵니다.
from app.core.config import get_app_settings


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        None,
    )


def get_app_settings():
    return Settings()


def get_url():
    return get_app_settings().database_url


def run_migrations_online():
    connectable = async_engine_from_config(
        configuration={
            "sqlalchemy.url": get_url(),
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        async with connectable.connect() as connection:
            # 동기 함수를 비동기 컨텍스트에서 실행
            await connection.run_sync(run_migrations)

    def run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())


run_migrations_online()
