from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.companies import validate_company_id
from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.users import validate_user_id
from app_psycopg.db.db import Database
from common.models import (
    UserCompanyLinkInput,
    UserCompanyLink,
)


# region UserCompanyLink


async def validate_user_company_link_input(
    db: Annotated[Database, Depends(get_db)],
    user_company_link_input: Annotated[UserCompanyLinkInput, Body(...)],
) -> UserCompanyLinkInput:
    # Validate user_id
    await validate_user_id(db=db, user_id=user_company_link_input.user_id)
    # Validate company_id
    await validate_company_id(db=db, company_id=user_company_link_input.company_id)

    # Check if the user already has 3 company links
    count: int = await db.get_user_company_links_count_by_user(
        user_id=user_company_link_input.user_id
    )
    if count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user_company_link_input.user_id}' already has the maximum of 3 company links.",
        )

    return user_company_link_input


async def validate_user_company_link(
    db: Annotated[Database, Depends(get_db)],
    user_id: UUID4,
    company_id: UUID4,
) -> UserCompanyLink:
    user_company_link: UserCompanyLink | None = await db.get_user_company_link(
        user_id=user_id, company_id=company_id
    )
    if user_company_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User-Company-Link '{user_id}/{company_id}' not found!",
        )
    return user_company_link


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
