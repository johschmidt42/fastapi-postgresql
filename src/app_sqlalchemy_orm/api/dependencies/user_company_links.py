from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_orm.api.dependencies.companies import validate_company_id
from app_sqlalchemy_orm.api.dependencies.users import validate_user_id
from app_sqlalchemy_orm.db.models import (
    users_companies_table,
)
from common.schemas import (
    UserCompanyLinkInput,
    UserCompanyLink,
)
from common.sqlalchemy.dependencies import get_db_session


# region UserCompanyLink


async def validate_user_company_link_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_company_link_input: Annotated[UserCompanyLinkInput, Body(...)],
) -> UserCompanyLinkInput:
    # Validate user_id
    await validate_user_id(session=session, user_id=user_company_link_input.user_id)
    # Validate company_id
    await validate_company_id(
        session=session, company_id=user_company_link_input.company_id
    )

    # Check if the user already has 3 company links
    query = (
        select(func.count())
        .select_from(users_companies_table)
        .where(users_companies_table.c.user_id == user_company_link_input.user_id)
    )
    result = await session.execute(query)
    count: int = result.scalar()

    if count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user_company_link_input.user_id}' already has the maximum of 3 company links.",
        )

    return user_company_link_input


async def validate_user_company_link(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: UUID4,
    company_id: UUID4,
) -> UserCompanyLink:
    query = select(users_companies_table).where(
        users_companies_table.c.user_id == user_id,
        users_companies_table.c.company_id == company_id,
    )
    result = await session.execute(query)
    user_company_link = result.first()

    if user_company_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User-Company-Link '{user_id}/{company_id}' not found!",
        )

    # Convert the row to a UserCompanyLink model
    return UserCompanyLink(
        user_id=user_company_link.user_id,
        company_id=user_company_link.company_id,
        created_at=user_company_link.created_at,
    )


async def validate_get_user_company_links(
    user_id: Optional[UUID4] = None,
    company_id: Optional[UUID4] = None,
) -> dict:
    """
    Validates that either user_id or company_id is provided, but not both.
    Returns a dict with the provided parameter.
    """
    if user_id is None and company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either user_id or company_id must be provided.",
        )

    if user_id is not None and company_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one of user_id or company_id can be provided, not both.",
        )

    return {"user_id": user_id, "company_id": company_id}


# endregion
