from typing import Annotated, List, Type, Optional, Set, Sequence, Any

from fastapi import APIRouter, Depends, status, Query
from pydantic import AfterValidator
from sqlalchemy import select, func, Select, Result, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_core.api.dependencies import (
    get_db_session,
    validate_order_input,
    validate_order_id,
)
from app_sqlalchemy_core.api.models import OrderInputValidated
from app_sqlalchemy_core.api.models import Order as OrderResponseModel
from app_sqlalchemy_core.api.pagination import (
    LimitOffsetPage,
    create_paginate_query,
    PaginationParams,
)
from app_sqlalchemy_core.api.sorting import (
    create_order_by_enum,
    validate_order_by_query_params,
    create_order_by_query,
)
from app_sqlalchemy_core.db.db_models import Order

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
