from typing import Annotated, Tuple, List

from fastapi import APIRouter, Depends, status, Path, Query
from pydantic import UUID4

from app_psycopg.api.dependencies import (
    get_db,
    validate_user_id,
    validate_company_id,
    validate_user_company_link_input,
    validate_user_company_link,
    validate_get_user_company_links,
)
from app_psycopg.api.models import (
    UserCompanyLinkInput,
    UserCompanyLinkWithCompany,
    UserCompanyLinkWithUser,
    UserCompanyLinkResponse,
)
from app_psycopg.api.pagination import LimitOffsetPage
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
    user_id: Annotated[UUID4, Path(...)],
    company_id: Annotated[UUID4, Path(...)],
) -> None:
    # Validate user_id
    await validate_user_id(db=db, user_id=user_id)
    # Validate company_id
    await validate_company_id(db=db, company_id=company_id)
    # Validate that the link exists
    await validate_user_company_link(db=db, user_id=user_id, company_id=company_id)

    # Delete the link
    await db.delete_user_company_link(user_id=user_id, company_id=company_id)


@router.get(
    path="",
    response_model=LimitOffsetPage[UserCompanyLinkWithCompany]
    | LimitOffsetPage[UserCompanyLinkWithUser],
    status_code=status.HTTP_200_OK,
)
async def get_user_company_links(
    db: Annotated[Database, Depends(get_db)],
    params: Annotated[dict, Depends(validate_get_user_company_links)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0, le=1000)] = 0,
) -> (
    LimitOffsetPage[UserCompanyLinkWithCompany]
    | LimitOffsetPage[UserCompanyLinkWithUser]
):
    # If user_id is provided, get companies linked to the user
    if params["user_id"] is not None:
        # Validate that the user exists
        await validate_user_id(db=db, user_id=params["user_id"])

        links: List[
            UserCompanyLinkWithCompany
        ] = await db.get_user_company_links_by_user(
            user_id=params["user_id"], limit=limit, offset=offset
        )
        total: int = await db.get_user_company_links_count_by_user(
            user_id=params["user_id"]
        )

        return LimitOffsetPage(
            items=links,
            items_count=len(links),
            total_count=total,
            limit=limit,
            offset=offset,
        )

    # If company_id is provided, get users linked to the company
    if params["company_id"] is not None:
        # Validate that the company exists
        await validate_company_id(db=db, company_id=params["company_id"])

        links: List[
            UserCompanyLinkWithUser
        ] = await db.get_user_company_links_by_company(
            company_id=params["company_id"], limit=limit, offset=offset
        )
        total: int = await db.get_user_company_links_count_by_company(
            company_id=params["company_id"]
        )

        return LimitOffsetPage(
            items=links,
            items_count=len(links),
            total_count=total,
            limit=limit,
            offset=offset,
        )
