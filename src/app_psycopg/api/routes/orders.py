from typing import Annotated, List, Type, Optional, Set

from fastapi import APIRouter, Depends, status, Query
from pydantic import AfterValidator, UUID4

from app_psycopg.api.dependencies import get_db, validate_order_input, validate_order_id
from app_psycopg.api.models import Order, OrderInputValidated
from app_psycopg.api.pagination import LimitOffsetPage
from app_psycopg.api.sorting import create_order_by_enum, validate_order_by_query_params
from app_psycopg.db.db import Database


router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)

order_sortable_fields: List[str] = [
    "amount",
]
OrderByOrder: Type = Annotated[
    Optional[Set[create_order_by_enum(order_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]


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
    limit: Annotated[int, Query(ge=1, lt=50)] = 10,
    offset: Annotated[int, Query(ge=0, lt=1000)] = 0,
    order_by: Annotated[OrderByOrder, Query()] = None,
) -> LimitOffsetPage[Order]:
    orders: List[Order] = await db.get_orders(
        limit=limit, offset=offset, order_by=order_by
    )
    total: int = await db.get_orders_count()

    return LimitOffsetPage(
        items=orders,
        items_count=len(orders),
        total_count=total,
        limit=limit,
        offset=offset,
    )


@router.delete(
    path="/{order_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order(
    db: Annotated[Database, Depends(get_db)],
    order: Annotated[Order, Depends(validate_order_id)],
) -> None:
    await db.delete_order(order.id)
