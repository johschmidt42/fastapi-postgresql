from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.db.db import Database
from common.schemas import (
    Company,
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
)


# region Company


async def validate_company_id(
    db: Annotated[Database, Depends(get_db)],
    company_id: UUID4,
) -> Company:
    company: Company | None = await db.get_company(company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_id}' not found!",
        )
    return company


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
