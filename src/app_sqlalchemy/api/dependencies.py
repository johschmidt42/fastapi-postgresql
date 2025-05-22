from typing import AsyncGenerator, Annotated

from fastapi import Request, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from sqlalchemy import select
from starlette import status

from app_sqlalchemy.api.models import (
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
)
from app_sqlalchemy.db.db_models import User, Document, Profession, Company, Order


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
    profession_id: str,
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
    session: Annotated[AsyncSession, Depends(get_db_session)], user_id: str
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
    # Validate profession_id
    await validate_profession_id(
        session=session, profession_id=user_input.profession_id
    )
    return user_input


async def validate_user_update(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_update: Annotated[UserUpdate, Body(...)],
) -> UserUpdate:
    # Validate profession_id
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
    session: Annotated[AsyncSession, Depends(get_db_session)], document_id: str
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
    order_id: str,
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
    company_id: str,
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


async def validate_user_company_link(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: str,
    company_id: str,
) -> tuple[User, Company]:
    user = await validate_user_id(session=session, user_id=user_id)
    company = await validate_company_id(session=session, company_id=company_id)

    # Check if the link exists
    stmt = select(User).filter(
        User.id == user_id, User.companies.any(Company.id == company_id)
    )
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link between user '{user_id}' and company '{company_id}' not found!",
        )

    return user, company


async def validate_user_company_link_input(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    link_input: Annotated[UserCompanyLinkInput, Body(...)],
) -> UserCompanyLinkInput:
    # Validate user_id and company_id
    await validate_user_id(session=session, user_id=link_input.user_id)
    await validate_company_id(session=session, company_id=link_input.company_id)
    return link_input


# endregion
