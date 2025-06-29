from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.users import validate_user_id
from app_psycopg.db.db import Database
from common.models import (
    OrderInput,
    User,
    OrderInputValidated,
    Order,
)


# region Order


async def validate_order_id(
    db: Annotated[Database, Depends(get_db)],
    order_id: UUID4,
) -> Order:
    order: Order | None = await db.get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found!",
        )
    return order


async def validate_order_input(
    db: Annotated[Database, Depends(get_db)],
    order_input: Annotated[OrderInput, Body(...)],
) -> OrderInputValidated:
    # Validate payer_id
    payer: User = await validate_user_id(db=db, user_id=order_input.payer_id)
    # Validate payee_id
    payee: User = await validate_user_id(db=db, user_id=order_input.payee_id)

    return OrderInputValidated(order_input=order_input, payer=payer, payee=payee)


# endregion
