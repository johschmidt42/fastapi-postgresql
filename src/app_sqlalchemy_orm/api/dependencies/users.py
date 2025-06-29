from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_orm.api.dependencies.professions import validate_profession_id
from app_sqlalchemy_orm.db.db_models import (
    User,
)
from common.models import (
    UserInput,
    UserUpdate,
    UserPatch,
)
from common.sqlalchemy.dependencies import get_db_session


# region User


async def validate_user_id(
    session: Annotated[AsyncSession, Depends(get_db_session)], user_id: UUID4
) -> User:
    user: User | None = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )

    return user


async def validate_user_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_input: Annotated[UserInput, Body(...)],
) -> UserInput:
    await validate_profession_id(
        session=session, profession_id=user_input.profession_id
    )
    return user_input


async def validate_user_update(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_update: Annotated[UserUpdate, Body(...)],
) -> UserUpdate:
    await validate_profession_id(
        session=session, profession_id=user_update.profession_id
    )
    return user_update


async def validate_user_patch(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_patch: Annotated[UserPatch, Body(...)],
) -> UserPatch:
    if user_patch.profession_id:
        await validate_profession_id(
            session=session, profession_id=user_patch.profession_id
        )
    return user_patch


# endregion
