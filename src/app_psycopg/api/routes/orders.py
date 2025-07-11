from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.orders import validate_order_input, validate_order_id
from app_psycopg.db.db import Database
from common.order_by_enums import OrderByOrder
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import Order, OrderInputValidated

router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.post(path="", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    db: Annotated[Database, Depends(get_db)],
    order_input_validated: Annotated[
        OrderInputValidated, Depends(validate_order_input)
    ],
) -> Order:
    order_id: UUID4 = await db.insert_order(order_input_validated.order_input)
    order: Order = await db.get_order(order_id)

    return Order.model_validate(order)


@router.get(path="/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def get_order(
    order: Annotated[Order, Depends(validate_order_id)],
) -> Order:
    return order


@router.get(
    path="",
    response_model=LimitOffsetPage[Order],
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    db: Annotated[Database, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByOrder, Query()] = None,
) -> LimitOffsetPage[Order]:
    orders: List[Order] = await db.get_orders(
        limit=pagination.limit, offset=pagination.offset, order_by=order_by
    )
    total: int = await db.get_orders_count()

    return LimitOffsetPage(
        items=orders,
        items_count=len(orders),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.delete(
    path="/{order_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order(
    db: Annotated[Database, Depends(get_db)],
    order: Annotated[Order, Depends(validate_order_id)],
) -> None:
    await db.delete_order(order.id)
