from typing import AsyncGenerator, Annotated, Optional

from fastapi import Request, Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from starlette import status

from app_sqlalchemy_orm.api.models import (
    OrderInput,
    OrderInputValidated,
    ProfessionInput,
    ProfessionUpdate,
    UserInput,
    UserUpdate,
    UserPatch,
    DocumentInput,
    DocumentUpdate,
    CompanyInput,
    CompanyUpdate,
    CompanyPatch,
    UserCompanyLinkInput,
    UserCompanyLink,
)
from app_sqlalchemy_orm.db.db_models import (
    User,
    Document,
    Profession,
    Company,
    Order,
    users_companies_table,
)


async def get_db_connection(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    async with request.state.conn_pool._engine.begin() as connection:
        yield connection


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.state.conn_pool._sessionmaker() as session:
        async with session.begin():
            yield session


# region Profession


async def validate_profession_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    profession_id: UUID4,
) -> Profession:
    profession: Profession | None = await session.get(Profession, profession_id)
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
    session: Annotated[AsyncSession, Depends(get_db_session)], user_id: UUID4
) -> User:
    user: User | None = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found!"
        )

    return user


async def validate_user_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_input: Annotated[UserInput, Body(...)],
) -> UserInput:
    await validate_profession_id(
        session=session, profession_id=user_input.profession_id
    )
    return user_input


async def validate_user_update(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_update: Annotated[UserUpdate, Body(...)],
) -> UserUpdate:
    await validate_profession_id(
        session=session, profession_id=user_update.profession_id
    )
    return user_update


async def validate_user_patch(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_patch: Annotated[UserPatch, Body(...)],
) -> UserPatch:
    if user_patch.profession_id:
        await validate_profession_id(
            session=session, profession_id=user_patch.profession_id
        )
    return user_patch


# endregion


# region Document


async def validate_document_id(
    session: Annotated[AsyncSession, Depends(get_db_session)], document_id: UUID4
) -> Document:
    document: Document | None = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found!",
        )

    return document


async def validate_document_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    document_input: Annotated[DocumentInput, Body(...)],
) -> DocumentInput:
    # Validate user_id
    await validate_user_id(session=session, user_id=document_input.user_id)
    return document_input


async def validate_document_update(
    document_update: Annotated[DocumentUpdate, Body(...)],
) -> DocumentUpdate:
    return document_update


# endregion


# region Order


async def validate_order_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    order_id: UUID4,
) -> Order:
    order: Order | None = await session.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found!",
        )
    return order


async def validate_order_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    order_input: Annotated[OrderInput, Body(...)],
) -> OrderInputValidated:
    # Validate payer_id
    payer: User = await validate_user_id(session=session, user_id=order_input.payer_id)
    # Validate payee_id
    payee: User = await validate_user_id(session=session, user_id=order_input.payee_id)

    return OrderInputValidated(order_input=order_input, payer=payer, payee=payee)


# endregion


# region Company


async def validate_company_id(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    company_id: UUID4,
) -> Company:
    company: Company | None = await session.get(Company, company_id)
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
