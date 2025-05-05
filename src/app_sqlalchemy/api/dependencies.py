from typing import AsyncGenerator, Annotated

from fastapi import Request, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from starlette import status

from app_sqlalchemy.api.models import OrderInput
from app_sqlalchemy.db.db_models import User


async def get_db_connection(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    async with request.state.conn_pool._engine.begin() as connection:
        yield connection


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.state.conn_pool._sessionmaker() as session:
        async with session.begin():
            yield session


async def validate_user_id(
    session: Annotated[AsyncSession, Depends(get_db_session)], user_id: str
) -> User:
    user: User | None = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )

    return user


async def validate_order_input(
    session: Annotated[AsyncSession, Depends(get_db_session)], order_input: Annotated[OrderInput, Body(...)],
) -> OrderInput:
    # Validate payer_id
    await validate_user_id(session=session, user_id=order_input.payer_id)
    # Validate payee_id
    await validate_user_id(session=session, user_id=order_input.payee_id)

    return order_input