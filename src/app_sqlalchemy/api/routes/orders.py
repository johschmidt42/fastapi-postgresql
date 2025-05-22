from typing import Annotated, List, Type, Optional, Set

from fastapi import APIRouter, Depends, status
from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy.api.dependencies import (
    get_db_session,
    validate_order_input,
)
from app_sqlalchemy.api.models import OrderInputValidated
from app_sqlalchemy.api.models import Order as OrderResponseModel
from app_sqlalchemy.api.sorting import (
    create_order_by_enum,
    validate_order_by_query_params,
)
from app_sqlalchemy.db.db_models import Order

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
