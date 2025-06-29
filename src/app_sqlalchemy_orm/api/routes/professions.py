from typing import Annotated, List, Type, Optional, Set, Sequence, Any

from fastapi import APIRouter, Depends, status, Query
from pydantic import AfterValidator
from sqlalchemy import select, func, Select, Result, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_orm.api.dependencies import (
    get_db_session,
    validate_profession_id,
    validate_profession_input,
    validate_profession_update,
)
from app_sqlalchemy_orm.api.models import (
    ProfessionInput,
    ProfessionUpdate,
)
from app_sqlalchemy_orm.api.models import Profession as ProfessionResponseModel

from common.pagination import LimitOffsetPage, PaginationParams
from common.sorting import create_order_by_enum, validate_order_by_query_params
from common.sqlalchemy.pagination import create_paginate_query

from app_sqlalchemy_orm.db.db_models import Profession
from common.sqlalchemy.sorting import create_order_by_query

router: APIRouter = APIRouter(
    tags=["Professions"],
    prefix="/professions",
)

profession_sortable_fields: List[str] = ["name"]
OrderByProfession: Type = Annotated[
    Optional[Set[create_order_by_enum(profession_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_profession(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    profession_input: Annotated[ProfessionInput, Depends(validate_profession_input)],
) -> str:
    profession: Profession = Profession(
        id=profession_input.id,
        name=profession_input.name,
        created_at=profession_input.created_at,
    )
    session.add(profession)
    return profession.id


@router.get(
    path="/{profession_id}",
    response_model=ProfessionResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_profession(
    profession: Annotated[Profession, Depends(validate_profession_id)],
) -> Profession:
    return profession


@router.get(
    path="",
    response_model=LimitOffsetPage[ProfessionResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_professions(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByProfession, Query()] = None,
) -> LimitOffsetPage[ProfessionResponseModel]:
    query: Select = create_paginate_query(
        query=select(Profession), limit=pagination.limit, offset=pagination.offset
    )

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=Profession
        )

    result: Result = await db_session.execute(query)

    professions: Sequence[Row | RowMapping | Any] = result.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(Profession)
    result = await db_session.execute(count_query)
    total = result.scalar()

    return LimitOffsetPage(
        items=professions,
        items_count=len(professions),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{profession_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_profession(
    profession: Annotated[Profession, Depends(validate_profession_id)],
    profession_update: Annotated[ProfessionUpdate, Depends(validate_profession_update)],
) -> str:
    profession.name = profession_update.name
    profession.last_updated_at = profession_update.last_updated_at
    return profession.id


@router.delete(
    path="/{profession_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_profession(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    profession: Annotated[Profession, Depends(validate_profession_id)],
) -> None:
    await session.delete(profession)
