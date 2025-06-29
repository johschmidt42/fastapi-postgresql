from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, Request, HTTPException, Body
from psycopg import Connection, AsyncConnection
from pydantic import UUID4
from starlette import status

from common.models import (
    OrderInput,
    UserInput,
    User,
    Profession,
    UserUpdate,
    UserPatch,
    ProfessionInput,
    ProfessionUpdate,
    OrderInputValidated,
    Order,
    Company,
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
    UserCompanyLinkInput,
    UserCompanyLink,
    DocumentInput,
    DocumentUpdate,
    Document,
)
from app_psycopg.db.db import Database


async def get_db_conn(request: Request) -> AsyncGenerator[Connection, None]:
    async with request.state.conn_pool.connection() as connection:
        yield connection


async def get_db(conn: Annotated[AsyncConnection, Depends(get_db_conn)]) -> Database:
    return Database(conn)


# region Profession


async def validate_profession_id(
    db: Annotated[Database, Depends(get_db)],
    profession_id: UUID4,
) -> Profession:
    profession: Profession | None = await db.get_profession(profession_id)
    if profession is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profession '{profession_id}' not found!",
        )
    return profession


async def validate_profession_input(
    profession_input: Annotated[ProfessionInput, Body(...)],
) -> ProfessionInput:
    return profession_input


async def validate_profession_update(
    profession_update: Annotated[ProfessionUpdate, Body(...)],
) -> ProfessionUpdate:
    return profession_update


# endregion

# region User


async def validate_user_id(
    db: Annotated[Database, Depends(get_db)],
    user_id: UUID4,
) -> User:
    user: User | None = await db.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )
    return user


async def validate_user_input(
    db: Annotated[Database, Depends(get_db)], user_input: UserInput
) -> UserInput:
    await validate_profession_id(db=db, profession_id=user_input.profession_id)
    return user_input


async def validate_user_update(
    db: Annotated[Database, Depends(get_db)],
    user_update: UserUpdate,
) -> UserUpdate:
    await validate_profession_id(db=db, profession_id=user_update.profession_id)
    return user_update


async def validate_user_patch(
    db: Annotated[Database, Depends(get_db)],
    user_patch: UserPatch,
) -> UserPatch:
    if user_patch.profession_id:
        await validate_profession_id(db=db, profession_id=user_patch.profession_id)
    return user_patch


# endregion

# region Document


async def validate_document_id(
    db: Annotated[Database, Depends(get_db)], document_id: UUID4
) -> Document:
    document: Document | None = await db.get_document(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found!",
        )
    return document


async def validate_document_input(
    db: Annotated[Database, Depends(get_db)],
    document_input: Annotated[DocumentInput, Body(...)],
) -> DocumentInput:
    # Validate user_id
    await validate_user_id(db=db, user_id=document_input.user_id)
    return document_input


async def validate_document_update(
    document_update: Annotated[DocumentUpdate, Body(...)],
) -> DocumentUpdate:
    return document_update


# endregion

# region Order


async def validate_order_id(
    db: Annotated[Database, Depends(get_db)],
    order_id: UUID4,
) -> Order:
    order: Order | None = await db.get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found!",
        )
    return order


async def validate_order_input(
    db: Annotated[Database, Depends(get_db)],
    order_input: Annotated[OrderInput, Body(...)],
) -> OrderInputValidated:
    # Validate payer_id
    payer: User = await validate_user_id(db=db, user_id=order_input.payer_id)
    # Validate payee_id
    payee: User = await validate_user_id(db=db, user_id=order_input.payee_id)

    return OrderInputValidated(order_input=order_input, payer=payer, payee=payee)


# endregion

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
