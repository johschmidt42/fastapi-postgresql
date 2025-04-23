from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from psycopg import Connection, AsyncConnection

from app_psycopg.db.db import Database


async def get_conn(request: Request) -> AsyncGenerator[Connection, None]:
    async with request.state.conn_pool.connection() as connection:
        yield connection


def get_db(conn: Annotated[AsyncConnection, Depends(get_conn)]) -> Database:
    return Database(conn)
