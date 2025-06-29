from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4
from sqlalchemy import select, func, Select, Result, RowMapping
from sqlalchemy import update, Update, delete, Delete, Insert
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_core.api.dependencies.companies import (
    get_db_session,
    validate_company_id,
    validate_company_input,
    validate_company_update,
    validate_company_patch,
)
from app_sqlalchemy_core.db.models import companies
from common.order_by_enums import OrderByCompany
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import (
    Company as CompanyResponseModel,
    CompanyUpdate,
    CompanyPatch,
)
from common.schemas import (
    CompanyInput,
    Company,
)
from common.sqlalchemy.pagination import create_paginate_query
from common.sqlalchemy.sorting import create_order_by_query

router: APIRouter = APIRouter(
    tags=["Companies"],
    prefix="/companies",
)


@router.post(path="", response_model=UUID4, status_code=status.HTTP_201_CREATED)
async def create_company(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company_input: Annotated[CompanyInput, Depends(validate_company_input)],
) -> UUID4:
    company: Company = Company(
        id=company_input.id,
        name=company_input.name,
        created_at=company_input.created_at,
    )

    stmt: Insert = (
        insert(companies)
        .values(company.model_dump())
        .on_conflict_do_nothing(index_elements=[companies.c.id])
        .returning(companies.c.id)
    )

    result: Result = await session.execute(stmt)

    return result.scalar_one()


@router.get(
    path="/{company_id}",
    response_model=CompanyResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_company(
    company: Annotated[Company, Depends(validate_company_id)],
) -> Company:
    return company


@router.get(
    path="",
    response_model=LimitOffsetPage[CompanyResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_companies(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByCompany, Query()] = None,
) -> LimitOffsetPage[CompanyResponseModel]:
    query: Select = create_paginate_query(
        query=select(companies), limit=pagination.limit, offset=pagination.offset
    )

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=list(order_by), model=companies
        )

    result: Result = await db_session.execute(query)

    rows: Sequence[RowMapping] = result.mappings().all()

    # Get total count
    count_query: Select = select(func.count()).select_from(companies)
    result: Result = await db_session.execute(count_query)
    total: int = result.scalar()

    return LimitOffsetPage(
        items=rows,
        items_count=len(rows),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK)
async def update_company(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company: Annotated[Company, Depends(validate_company_id)],
    company_update: Annotated[CompanyUpdate, Depends(validate_company_update)],
) -> UUID4:
    stmt: Update = (
        update(companies)
        .where(companies.c.id == company.id)  # type: ignore[arg-type]
        .values(
            name=company_update.name, last_updated_at=company_update.last_updated_at
        )
        .returning(companies.c.id)
    )
    result: Result = await session.execute(stmt)
    return result.scalar_one()


@router.patch(
    path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK
)
async def patch_company(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company: Annotated[Company, Depends(validate_company_id)],
    company_patch: Annotated[CompanyPatch, Depends(validate_company_patch)],
) -> UUID4:
    values: dict = {"last_updated_at": company_patch.last_updated_at}

    if company_patch.name is not None:
        values["name"] = func.coalesce(company_patch.name, companies.c.name)

    stmt: Update = (
        update(companies)
        .where(companies.c.id == company.id)  # type: ignore[arg-type]
        .values(values)
        .returning(companies.c.id)
    )

    result: Result = await session.execute(stmt)
    return result.scalar_one()


@router.delete(
    path="/{company_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_company(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company: Annotated[Company, Depends(validate_company_id)],
) -> None:
    stmt: Delete = delete(companies).where(companies.c.id == company.id)  # type: ignore[arg-type]
    await session.execute(stmt)
    return None
