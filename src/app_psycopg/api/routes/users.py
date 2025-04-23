from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from app_psycopg.db.db import Database
from app_psycopg.db.db_models import User, UserInput, UserUpdate
from app_psycopg.api.dependencies import get_db

router: APIRouter = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router.post(path="", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[Database, Depends(get_db)],
    user_input: Annotated[UserInput, Body(...)],
) -> User:
    user_id: str = await db.insert_user(user_input)
    user: User = await db.get_user(user_id)
    return user


@router.get(path="/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(
    db: Annotated[Database, Depends(get_db)],
    user_id: Annotated[str, Path(...)],
) -> User:
    user: None | User = await db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.put(path="/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    db: Annotated[Database, Depends(get_db)],
    user_id: Annotated[UUID, Path(...)],
    update: Annotated[UserUpdate, Body(...)],
) -> User:
    user_id: str = await db.update_user(user_id, update)
    return await db.get_user(user_id)


@router.delete(
    path="/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db: Annotated[Database, Depends(get_db)],
    user_id: Annotated[UUID, Path(...)],
) -> None:
    await db.delete_user(user_id)
