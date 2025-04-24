from typing import Annotated

from fastapi import APIRouter, Depends, status

from app_psycopg.api.dependencies import get_db, validate_order_input
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import Order, OrderInput

router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.post(path="", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    db: Annotated[Database, Depends(get_db)],
    order_input: OrderInput = Depends(validate_order_input),
) -> Order:
    order_id: str = await db.insert_order(order_input)
    order: Order = await db.get_order(order_id)
    return order
