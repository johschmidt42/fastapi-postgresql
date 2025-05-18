from typing import Annotated, List, Type, Optional, Set

from fastapi import APIRouter, Body, Depends, status, Query
from pydantic import AfterValidator

from app_psycopg.api.dependencies import get_db, validate_user_id
from app_psycopg.api.models import (
    UserInput,
    UserUpdate,
    UserResponseModel,
)
from app_psycopg.api.pagination import LimitOffsetPage
from app_psycopg.api.sorting import create_order_by_enum, validate_order_by_query_params
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import User

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
    db: Annotated[Database, Depends(get_db)],
    user_input: Annotated[UserInput, Body(...)],
) -> str:
    user_id: str = await db.insert_user(user_input)
    user: User = await db.get_user(user_id)
    return user.id


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
    db: Annotated[Database, Depends(get_db)],
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[OrderByUser, Query()] = None,
) -> LimitOffsetPage[UserResponseModel]:
    users: List[User] = await db.get_users(
        limit=limit, offset=offset, order_by=order_by
    )
    total: int = await db.get_users_count()

    items: List[UserResponseModel] = [
        UserResponseModel.model_validate(user) for user in users
    ]

    return LimitOffsetPage(
        items=items,
        items_count=len(items),
        total_count=total,
        limit=limit,
        offset=offset,
    )


@router.put(path="/{user_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_user(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[User, Depends(validate_user_id)],
    update: Annotated[UserUpdate, Body(...)],
) -> str:
    user_id: str = await db.update_user(id=user.id, update=update)
    user: User = await db.get_user(user_id)
    return user.id


@router.delete(
    path="/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[User, Depends(validate_user_id)],
) -> None:
    await db.delete_user(user.id)
