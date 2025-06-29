from typing import Annotated, List, Any, Type, Optional, Set

from fastapi import APIRouter, Body, Depends, status, Query
from pydantic import AfterValidator
from sqlalchemy import Select, Result, Sequence, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlalchemy_orm.api.dependencies.users import validate_user_id
from common.schemas import User as UserResponseModel
from common.schemas import UserInput, UserUpdate
from common.pagination import LimitOffsetPage, PaginationParams
from common.sorting import create_order_by_enum, validate_order_by_query_params
from common.sqlalchemy.dependencies import get_db_session
from common.sqlalchemy.pagination import create_paginate_query

from app_sqlalchemy_orm.db.models import User
from common.sqlalchemy.sorting import create_order_by_query

router: APIRouter = APIRouter(
    tags=["Users"],
    prefix="/users",
)

user_sortable_fields: List[str] = ["name", "created_at", "last_updated_at"]
OrderByUser: Type = Annotated[
    Optional[Set[create_order_by_enum(user_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_input: Annotated[UserInput, Body(...)],
) -> str:
    new_user: User = User(
        id=user_input.id,
        name=user_input.name,
        created_at=user_input.created_at,
    )

    db_session.add(new_user)

    return new_user.id


@router.get(
    path="/{user_id}", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def get_user(
    user: Annotated[User, Depends(validate_user_id)],
) -> UserResponseModel:
    return UserResponseModel.model_validate(user)


@router.get(
    path="",
    response_model=LimitOffsetPage[UserResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByUser, Query()] = None,
) -> LimitOffsetPage[UserResponseModel]:
    query: Select = select(User)

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=User
        )

    result: Result = await db_session.execute(
        create_paginate_query(
            query=query, limit=pagination.limit, offset=pagination.offset
        )
    )
    users: Sequence[Any] = result.scalars().all()

    count_query: Select = select(func.count()).select_from(query.subquery())
    total_count_result: Result = await db_session.execute(count_query)
    total_count: int = total_count_result.scalar_one()

    return LimitOffsetPage(
        items=[UserResponseModel.model_validate(user) for user in users],
        items_count=len(users),
        total_count=total_count,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{user_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_user(
    user: Annotated[User, Depends(validate_user_id)],
    update: Annotated[UserUpdate, Body(...)],
) -> str:
    user.name = update.name
    user.last_updated_at = update.last_updated_at

    return user.id


@router.delete(
    path="/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(validate_user_id)],
) -> None:
    await db_session.delete(user)
