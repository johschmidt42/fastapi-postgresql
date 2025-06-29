from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.professions import validate_profession_id
from app_psycopg.db.db import Database
from common.schemas import (
    UserInput,
    User,
    UserUpdate,
    UserPatch,
)


# region User


async def validate_user_id(
    db: Annotated[Database, Depends(get_db)],
    user_id: UUID4,
) -> User:
    user: User | None = await db.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )
    return user


async def validate_user_input(
    db: Annotated[Database, Depends(get_db)], user_input: UserInput
) -> UserInput:
    await validate_profession_id(db=db, profession_id=user_input.profession_id)
    return user_input


async def validate_user_update(
    db: Annotated[Database, Depends(get_db)],
    user_update: UserUpdate,
) -> UserUpdate:
    await validate_profession_id(db=db, profession_id=user_update.profession_id)
    return user_update


async def validate_user_patch(
    db: Annotated[Database, Depends(get_db)],
    user_patch: UserPatch,
) -> UserPatch:
    if user_patch.profession_id:
        await validate_profession_id(db=db, profession_id=user_patch.profession_id)
    return user_patch


# endregion
