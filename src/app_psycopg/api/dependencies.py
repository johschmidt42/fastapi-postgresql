from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request, HTTPException, Body
from psycopg import Connection, AsyncConnection
from starlette import status

from app_psycopg.db.db import Database
from app_psycopg.db.db_models import User, OrderInput


async def get_conn(request: Request) -> AsyncGenerator[Connection, None]:
    async with request.state.conn_pool.connection() as connection:
        yield connection


def get_db(conn: Annotated[AsyncConnection, Depends(get_conn)]) -> Database:
    return Database(conn)


async def validate_user_id(
    db: Annotated[Database, Depends(get_db)],
    user_id: str,
) -> User:
    user: User | None = await db.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )
    return user


async def validate_order_input(
    db: Annotated[Database, Depends(get_db)],
    order_input: Annotated[OrderInput, Body(...)],
) -> OrderInput:
    # Validate payer_id
    await validate_user_id(db=db, user_id=order_input.payer_id)
    # Validate payee_id
    await validate_user_id(db=db, user_id=order_input.payee_id)

    return order_input
