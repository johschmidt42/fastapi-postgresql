from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_orm.api.dependencies.users import validate_user_id
from app_sqlalchemy_orm.db.db_models import (
    User,
    Order,
)
from common.models import (
    OrderInput,
    OrderInputValidated,
)
from common.sqlalchemy.dependencies import get_db_session


# region Order


async def validate_order_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    order_id: UUID4,
) -> Order:
    order: Order | None = await session.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found!",
        )
    return order


async def validate_order_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    order_input: Annotated[OrderInput, Body(...)],
) -> OrderInputValidated:
    # Validate payer_id
    payer: User = await validate_user_id(session=session, user_id=order_input.payer_id)
    # Validate payee_id
    payee: User = await validate_user_id(session=session, user_id=order_input.payee_id)

    return OrderInputValidated(order_input=order_input, payer=payer, payee=payee)


# endregion
