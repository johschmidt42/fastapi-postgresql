from typing import Annotated, Tuple, List

from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from app_psycopg.api.dependencies.companies import validate_company_id
from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.user_company_links import (
    validate_user_company_link_input,
    validate_user_company_link,
    validate_get_user_company_links,
)
from app_psycopg.api.dependencies.users import validate_user_id
from common.models import (
    UserCompanyLinkInput,
    UserCompanyLinkWithCompany,
    UserCompanyLinkWithUser,
    UserCompanyLinkResponse,
)
from common.pagination import LimitOffsetPage, PaginationParams
from app_psycopg.db.db import Database

router: APIRouter = APIRouter(
    tags=["User-Company Links"],
    prefix="/user-company-links",
)


@router.post(
    path="", response_model=UserCompanyLinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_company_link(
    db: Annotated[Database, Depends(get_db)],
    user_company_link_input: Annotated[
        UserCompanyLinkInput, Depends(validate_user_company_link_input)
    ],
) -> UserCompanyLinkResponse:
    result: Tuple[UUID4, UUID4] = await db.insert_user_company_link(
        data=user_company_link_input
    )
    return UserCompanyLinkResponse(user_id=result[0], company_id=result[1])


@router.delete(
    path="/{user_id}/{company_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_company_link(
    db: Annotated[Database, Depends(get_db)],
    user: Annotated[UUID4, Depends(validate_user_id)],
    company: Annotated[UUID4, Depends(validate_company_id)],
) -> None:
    # Validate that the link exists
    await validate_user_company_link(db=db, user_id=user.id, company_id=company.id)

    # Delete the link
    await db.delete_user_company_link(user_id=user.id, company_id=company.id)


@router.get(
    path="",
    response_model=LimitOffsetPage[UserCompanyLinkWithCompany]
    | LimitOffsetPage[UserCompanyLinkWithUser],
    status_code=status.HTTP_200_OK,
)
async def get_user_company_links(
    db: Annotated[Database, Depends(get_db)],
    params: Annotated[dict, Depends(validate_get_user_company_links)],
    pagination: Annotated[PaginationParams, Depends()],
) -> (
    LimitOffsetPage[UserCompanyLinkWithCompany]
    | LimitOffsetPage[UserCompanyLinkWithUser]
):
    # The validate_get_user_company_links dependency ensures that exactly one of
    # user_id or company_id is provided, so we can safely use an if-else structure

    # If user_id is provided, get companies linked to the user
    if params["user_id"] is not None:
        # Validate that the user exists
        await validate_user_id(db=db, user_id=params["user_id"])

        links: List[
            UserCompanyLinkWithCompany
        ] = await db.get_user_company_links_by_user(
            user_id=params["user_id"], limit=pagination.limit, offset=pagination.offset
        )
        total: int = await db.get_user_company_links_count_by_user(
            user_id=params["user_id"]
        )

        return LimitOffsetPage[UserCompanyLinkWithCompany](
            items=links,
            items_count=len(links),
            total_count=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    # Else company_id is provided (guaranteed by validate_get_user_company_links)
    else:
        # We know company_id is not None here because validate_get_user_company_links
        # ensures that exactly one of user_id or company_id is provided
        company_id = params["company_id"]
        # Validate that the company exists
        await validate_company_id(db=db, company_id=company_id)

        links: List[
            UserCompanyLinkWithUser
        ] = await db.get_user_company_links_by_company(
            company_id=company_id, limit=pagination.limit, offset=pagination.offset
        )
        total: int = await db.get_user_company_links_count_by_company(
            company_id=company_id
        )

        return LimitOffsetPage[UserCompanyLinkWithUser](
            items=links,
            items_count=len(links),
            total_count=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )
