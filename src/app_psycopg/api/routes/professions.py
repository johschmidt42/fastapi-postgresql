from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.professions import (
    validate_profession_input,
    validate_profession_id,
    validate_profession_update,
)
from app_psycopg.db.db import Database
from common.order_by_enums import OrderByProfession
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import (
    ProfessionInput,
    Profession,
    ProfessionUpdate,
)

router: APIRouter = APIRouter(
    tags=["Professions"],
    prefix="/professions",
)


@router.post(path="", response_model=UUID4, status_code=status.HTTP_201_CREATED)
async def create_profession(
    db: Annotated[Database, Depends(get_db)],
    profession_input: Annotated[ProfessionInput, Depends(validate_profession_input)],
) -> UUID4:
    profession_id: UUID4 = await db.insert_profession(profession_input)
    return profession_id


@router.get(
    path="/{profession_id}",
    response_model=Profession,
    status_code=status.HTTP_200_OK,
)
async def get_profession(
    profession: Annotated[Profession, Depends(validate_profession_id)],
) -> Profession:
    return profession


@router.get(
    path="",
    response_model=LimitOffsetPage[Profession],
    status_code=status.HTTP_200_OK,
)
async def get_professions(
    db: Annotated[Database, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByProfession, Query()] = None,
) -> LimitOffsetPage[Profession]:
    professions: List[Profession] = await db.get_professions(
        limit=pagination.limit, offset=pagination.offset, order_by=order_by
    )
    total: int = await db.get_professions_count()

    return LimitOffsetPage(
        items=professions,
        items_count=len(professions),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(
    path="/{profession_id}", response_model=UUID4, status_code=status.HTTP_200_OK
)
async def update_profession(
    db: Annotated[Database, Depends(get_db)],
    profession: Annotated[Profession, Depends(validate_profession_id)],
    profession_update: Annotated[ProfessionUpdate, Depends(validate_profession_update)],
) -> UUID4:
    profession_id: UUID4 = await db.update_profession(
        id=profession.id, update=profession_update
    )
    return profession_id


@router.delete(
    path="/{profession_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_profession(
    db: Annotated[Database, Depends(get_db)],
    profession: Annotated[Profession, Depends(validate_profession_id)],
) -> None:
    await db.delete_profession(profession.id)
