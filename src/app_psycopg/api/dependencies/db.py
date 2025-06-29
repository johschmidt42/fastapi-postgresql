from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from psycopg import Connection, AsyncConnection

from app_psycopg.db.db import Database


async def get_db_conn(request: Request) -> AsyncGenerator[Connection, None]:
    """
    Provides a single-use asynchronous database connection from the request's connection pool.

    Args:
        request (Request): The incoming FastAPI request containing the connection pool.

    Yields:
        AsyncGenerator[Connection, None]: An asynchronous generator yielding a database connection.
    """

    async with request.state.conn_pool.connection() as connection:
        yield connection


async def get_db(conn: Annotated[AsyncConnection, Depends(get_db_conn)]) -> Database:
    """
    Creates a Database instance using the provided asynchronous connection.

    Args:
        conn (AsyncConnection): The database connection obtained via dependency injection.

    Returns:
        Database: An instance of the Database wrapper using the given connection.
    """

    return Database(conn)
