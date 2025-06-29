from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4

from app_psycopg.api.dependencies.companies import (
    validate_company_input,
    validate_company_id,
    validate_company_update,
    validate_company_patch,
)
from app_psycopg.api.dependencies.db import get_db
from app_psycopg.db.db import Database
from common.order_by_enums import OrderByCompany
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import (
    CompanyInput,
    Company,
    CompanyUpdate,
    CompanyPatch,
)

router: APIRouter = APIRouter(
    tags=["Companies"],
    prefix="/companies",
)


@router.post(path="", response_model=UUID4, status_code=status.HTTP_201_CREATED)
async def create_company(
    db: Annotated[Database, Depends(get_db)],
    company_input: Annotated[CompanyInput, Depends(validate_company_input)],
) -> UUID4:
    company_id: UUID4 = await db.insert_company(company_input)
    return company_id


@router.get(
    path="/{company_id}",
    response_model=Company,
    status_code=status.HTTP_200_OK,
)
async def get_company(
    company: Annotated[Company, Depends(validate_company_id)],
) -> Company:
    return company


@router.get(
    path="",
    response_model=LimitOffsetPage[Company],
    status_code=status.HTTP_200_OK,
)
async def get_companies(
    db: Annotated[Database, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByCompany, Query()] = None,
) -> LimitOffsetPage[Company]:
    companies: List[Company] = await db.get_companies(
        limit=pagination.limit, offset=pagination.offset, order_by=order_by
    )
    total: int = await db.get_companies_count()

    return LimitOffsetPage(
        items=companies,
        items_count=len(companies),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK)
async def update_company(
    db: Annotated[Database, Depends(get_db)],
    company: Annotated[Company, Depends(validate_company_id)],
    company_update: Annotated[CompanyUpdate, Depends(validate_company_update)],
) -> UUID4:
    company_id: UUID4 = await db.update_company(id=company.id, update=company_update)
    return company_id


@router.patch(
    path="/{company_id}", response_model=UUID4, status_code=status.HTTP_200_OK
)
async def patch_company(
    db: Annotated[Database, Depends(get_db)],
    company: Annotated[Company, Depends(validate_company_id)],
    company_patch: Annotated[CompanyPatch, Depends(validate_company_patch)],
) -> UUID4:
    company_id: UUID4 = await db.patch_company(id=company.id, patch=company_patch)
    return company_id


@router.delete(
    path="/{company_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_company(
    db: Annotated[Database, Depends(get_db)],
    company: Annotated[Company, Depends(validate_company_id)],
) -> None:
    await db.delete_company(company.id)
