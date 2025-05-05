from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy.api.dependencies import get_db_session, validate_order_input
from app_sqlalchemy.api.models import OrderInput, OrderResponseModel

router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.post(
    path="", response_model=OrderResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_order(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    order_input: OrderInput = Depends(validate_order_input),
) -> OrderResponseModel:
    # order_id: str = await db.insert_order(order_input)
    # order: Order = await db.get_order(order_id)
    return ...
