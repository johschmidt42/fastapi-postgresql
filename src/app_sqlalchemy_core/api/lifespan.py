from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app_sqlalchemy_core.db.db import DatabaseEngine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    conn_info: str = "postgresql+psycopg://admin:admin@localhost:5432/postgres"
    async with (
        DatabaseEngine(
            echo=True,
            host=conn_info,
            pool_size=2,
            max_overflow=0,
            pool_pre_ping=True,  # https://docs.sqlalchemy.org/en/14/core/pooling.html#dealing-with-disconnects
        ) as conn_pool
    ):
        yield {"conn_pool": conn_pool}

    print("Shutdown")
