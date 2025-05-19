from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request, HTTPException, Body
from psycopg import Connection, AsyncConnection
from pydantic import UUID4
from starlette import status

from app_psycopg.api.models import (
    OrderInput,
    UserInput,
    User,
    Profession,
    UserUpdate,
    UserPatch,
    ProfessionInput,
    ProfessionUpdate,
    OrderInputValidated,
)
from app_psycopg.db.db import Database
from app_psycopg.api.models import Document


async def get_conn(request: Request) -> AsyncGenerator[Connection, None]:
    async with request.state.conn_pool.connection() as connection:
        yield connection


async def get_db(conn: Annotated[AsyncConnection, Depends(get_conn)]) -> Database:
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
    user_id: str,
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
    db: Annotated[Database, Depends(get_db)], document_id: str
) -> Document:
    document: Document | None = await db.get_document(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found!",
        )
    return document


# endregion

# region Order


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
