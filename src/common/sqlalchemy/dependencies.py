from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection


async def get_db_connection(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """
    Provides an asynchronous SQLAlchemy connection from the request's engine.

    Args:
        request (Request): The incoming FastAPI request containing the connection pool.

    Yields:
        AsyncGenerator[AsyncConnection, None]: An asynchronous generator yielding a database connection.
    """

    async with request.state.conn_pool._engine.begin() as connection:
        yield connection


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous SQLAlchemy session with an active transaction.

    Args:
        request (Request): The incoming FastAPI request containing the sessionmaker.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous generator yielding a database session.
    """

    async with request.state.conn_pool._sessionmaker() as session:
        async with session.begin():
            yield session
