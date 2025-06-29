from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.users import (
    validate_user_input,
    validate_user_id,
    validate_user_update,
    validate_user_patch,
)
from app_psycopg.db.db import Database
from common.order_by_enums import OrderByUser
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import (
    UserInput,
    UserUpdate,
    User,
    UserPatch,
)

router: APIRouter = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router.post(path="", response_model=UUID4, status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[Database, Depends(get_db)],
    user_input: Annotated[UserInput, Depends(validate_user_input)],
) -> UUID4:
    user_id: UUID4 = await db.insert_user(user_input)
    return user_id


@router.get(path="/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(
    user: Annotated[User, Depends(validate_user_id)],
) -> User:
    return user


@router.get(
    path="",
    response_model=LimitOffsetPage[User],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    db: Annotated[Database, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByUser, Query()] = None,
) -> LimitOffsetPage[User]:
    users: List[User] = await db.get_users(
        limit=pagination.limit, offset=pagination.offset, order_by=order_by
    )
    total: int = await db.get_users_count()

    return LimitOffsetPage(
        items=users,
        items_count=len(users),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{user_id}", response_model=UUID4, status_code=status.HTTP_200_OK)
async def update_user(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[User, Depends(validate_user_id)],
    user_update: Annotated[UserUpdate, Depends(validate_user_update)],
) -> UUID4:
    user_id: UUID4 = await db.update_user(id=user.id, update=user_update)
    return user_id


@router.patch(path="/{user_id}", response_model=UUID4, status_code=status.HTTP_200_OK)
async def patch_user(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[User, Depends(validate_user_id)],
    user_patch: Annotated[UserPatch, Depends(validate_user_patch)],
) -> UUID4:
    user_id: UUID4 = await db.patch_user(id=user.id, patch=user_patch)
    return user_id


@router.delete(
    path="/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[User, Depends(validate_user_id)],
) -> None:
    await db.delete_user(user.id)
