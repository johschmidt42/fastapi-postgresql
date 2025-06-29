from typing import Annotated, Sequence, Any

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select, func, Select, Result, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_orm.api.dependencies.orders import (
    validate_order_input,
    validate_order_id,
)
from common.order_by_enums import OrderByOrder

from common.schemas import OrderInputValidated
from common.schemas import Order as OrderResponseModel
from common.pagination import LimitOffsetPage, PaginationParams
from common.sqlalchemy.dependencies import get_db_session
from common.sqlalchemy.pagination import create_paginate_query

from app_sqlalchemy_orm.db.models import Order
from common.sqlalchemy.sorting import create_order_by_query

router: APIRouter = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.post(
    path="", response_model=OrderResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_order(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    validated_order_input: Annotated[
        OrderInputValidated, Depends(validate_order_input)
    ],
) -> OrderResponseModel:
    new_order: Order = Order(
        id=validated_order_input.order_input.id,
        amount=validated_order_input.order_input.amount,
        payer=validated_order_input.payer,
        payee=validated_order_input.payee,
    )

    db_session.add(new_order)

    return OrderResponseModel.model_validate(new_order)


@router.get(
    path="/{order_id}",
    response_model=OrderResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order: Annotated[Order, Depends(validate_order_id)],
) -> OrderResponseModel:
    return OrderResponseModel.model_validate(order)


@router.get(
    path="",
    response_model=LimitOffsetPage[OrderResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByOrder, Query()] = None,
) -> LimitOffsetPage[OrderResponseModel]:
    query: Select = create_paginate_query(
        query=select(Order), limit=pagination.limit, offset=pagination.offset
    )

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=Order
        )

    result: Result = await db_session.execute(query)

    orders: Sequence[Row | RowMapping | Any] = result.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(Order)
    result = await db_session.execute(count_query)
    total = result.scalar()

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
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    order: Annotated[Order, Depends(validate_order_id)],
) -> None:
    await db_session.delete(order)
