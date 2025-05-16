from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, status, Query

from app_psycopg.api.dependencies import get_db, validate_user_id
from app_psycopg.api.models import UserInput, UserUpdate, UserResponseModel
from app_psycopg.api.pagination import LimitOffsetPage
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import User

router: APIRouter = APIRouter(
    tags=["Users"],
    prefix="/users",
)


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
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
) -> LimitOffsetPage[UserResponseModel]:
    users: List[User] = await db.get_users(limit=limit, offset=offset)
    total: int = await db.get_users_count() if users else 0

    items: List[UserResponseModel] = [
        UserResponseModel.model_validate(user) for user in users
    ]

    return LimitOffsetPage(
        items=items,
        total=total,
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
