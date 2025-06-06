from typing import Annotated, List, Any, Type, Optional, Set

from fastapi import APIRouter, Body, Depends, status, Query
from pydantic import AfterValidator
from sqlalchemy import Select, Result, Sequence, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlalchemy.api.dependencies import validate_user_id, get_db_session
from app_sqlalchemy.api.models import UserResponseModel, UserInput, UserUpdate
from app_sqlalchemy.api.sorting import (
    create_order_by_enum,
    validate_order_by_query_params,
    create_order_by_query,
)
from app_sqlalchemy.db.db_models import User

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
    path="", response_model=List[UserResponseModel], status_code=status.HTTP_200_OK
)
async def get_users(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[OrderByUser, Query()] = None,
) -> List[UserResponseModel]:
    query: Select = select(User).limit(limit).offset(offset)

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=User
        )

    result: Result = await db_session.execute(query)

    users: Sequence[Row | RowMapping | Any] = result.scalars().all()

    return [UserResponseModel.model_validate(user) for user in users]


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
