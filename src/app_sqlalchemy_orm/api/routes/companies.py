from typing import Annotated, Sequence, Any

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4
from sqlalchemy import select, func, Select, Result, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_orm.api.dependencies.companies import (
    validate_company_input,
    validate_company_id,
    validate_company_update,
    validate_company_patch,
)
from common.order_by_enums import OrderByCompany
from common.schemas import (
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
)
from common.schemas import Company as CompanyResponseModel


from app_sqlalchemy_orm.db.models import Company
from common.pagination import LimitOffsetPage, PaginationParams
from common.sqlalchemy.dependencies import get_db_session
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
    session.add(company)
    return company.id


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
        query=select(Company), limit=pagination.limit, offset=pagination.offset
    )

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=Company
        )

    result: Result = await db_session.execute(query)

    companies: Sequence[Row | RowMapping | Any] = result.scalars().all()

    # Get total count
    count_query: Select = select(func.count()).select_from(Company)
    result: Result = await db_session.execute(count_query)
    total: int = result.scalar()

    return LimitOffsetPage(
        items=companies,
        items_count=len(companies),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK)
async def update_company(
    company: Annotated[Company, Depends(validate_company_id)],
    company_update: Annotated[CompanyUpdate, Depends(validate_company_update)],
) -> UUID4:
    company.name = company_update.name
    company.last_updated_at = company_update.last_updated_at
    return company.id


@router.patch(
    path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK
)
async def patch_company(
    company: Annotated[Company, Depends(validate_company_id)],
    company_patch: Annotated[CompanyPatch, Depends(validate_company_patch)],
) -> UUID4:
    if company_patch.name is not None:
        company.name = company_patch.name
    company.last_updated_at = company_patch.last_updated_at
    return company.id


@router.delete(
    path="/{company_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_company(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company: Annotated[Company, Depends(validate_company_id)],
) -> None:
    await session.delete(company)
