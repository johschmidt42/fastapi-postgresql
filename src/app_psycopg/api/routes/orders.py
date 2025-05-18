from typing import Annotated

from fastapi import APIRouter, Depends, status

from app_psycopg.api.dependencies import get_db, validate_order_input, ValidatedOrder
from app_psycopg.api.models import OrderResponseModel
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import Order

router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.post(
    path="", response_model=OrderResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_order(
    db: Annotated[Database, Depends(get_db)],
    validated_order_input: Annotated[ValidatedOrder, Depends(validate_order_input)],
) -> OrderResponseModel:
    order_id: str = await db.insert_order(validated_order_input.order_input)
    order: Order = await db.get_order(order_id)

    return OrderResponseModel.model_validate(order)
