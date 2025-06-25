from typing import AsyncGenerator, Annotated

from fastapi import Request, Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy import select, Result, Select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from starlette import status

from app_sqlalchemy_core.api.models import (
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
    Company,
)
from app_sqlalchemy_core.db.db_models import companies


async def get_db_connection(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    async with request.state.conn_pool._engine.begin() as connection:
        yield connection


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.state.conn_pool._sessionmaker() as session:
        async with session.begin():
            yield session


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
