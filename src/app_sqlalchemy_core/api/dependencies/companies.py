from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy import select, Result, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_core.db.models import companies
from common.schemas import (
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
    Company,
)
from common.sqlalchemy.dependencies import get_db_session


# region Company


async def validate_company_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company_id: UUID4,
) -> Company:
    stmt: Select = select(companies).where(companies.c.id == company_id)  # type: ignore[arg-type]
    result: Result = await session.execute(statement=stmt)

    company: dict | None = result.mappings().one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_id}' not found!",
        )
    return Company.model_validate(company)


async def validate_company_input(
    company_input: Annotated[CompanyInput, Body(...)],
) -> CompanyInput:
    return company_input


async def validate_company_update(
    company_update: Annotated[CompanyUpdate, Body(...)],
) -> CompanyUpdate:
    return company_update


async def validate_company_patch(
    company_patch: Annotated[CompanyPatch, Body(...)],
) -> CompanyPatch:
    return company_patch


# endregion
