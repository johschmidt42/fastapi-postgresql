from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_orm.db.db_models import (
    Profession,
)
from common.models import (
    ProfessionInput,
    ProfessionUpdate,
)
from common.sqlalchemy.dependencies import get_db_session


# region Profession


async def validate_profession_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    profession_id: UUID4,
) -> Profession:
    profession: Profession | None = await session.get(Profession, profession_id)
    if profession is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profession '{profession_id}' not found!",
        )
    return profession


async def validate_profession_input(
    profession_input: Annotated[ProfessionInput, Body(...)],
) -> ProfessionInput:
    return profession_input


async def validate_profession_update(
    profession_update: Annotated[ProfessionUpdate, Body(...)],
) -> ProfessionUpdate:
    return profession_update


# endregion
