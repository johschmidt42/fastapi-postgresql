from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.db.db import Database
from common.models import (
    Profession,
    ProfessionInput,
    ProfessionUpdate,
)


# region Profession


async def validate_profession_id(
    db: Annotated[Database, Depends(get_db)],
    profession_id: UUID4,
) -> Profession:
    profession: Profession | None = await db.get_profession(profession_id)
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
