from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from psycopg.conninfo import make_conninfo
from psycopg_pool import AsyncConnectionPool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    conn_info: str = make_conninfo(
        host="localhost", port=5432, dbname="postgres", password="admin", user="admin"
    )
    async with (
        AsyncConnectionPool(
            conninfo=conn_info,
            min_size=1,
            max_size=2,
            check=AsyncConnectionPool.check_connection,  # https://www.psycopg.org/psycopg3/docs/advanced/pool.html#connection-quality
        ) as conn_pool
    ):
        yield {"conn_pool": conn_pool}

    print("Shutdown")
