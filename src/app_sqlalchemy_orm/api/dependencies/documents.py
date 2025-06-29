from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_sqlalchemy_orm.api.dependencies.users import validate_user_id
from app_sqlalchemy_orm.db.db_models import (
    Document,
)
from common.schemas import (
    DocumentInput,
    DocumentUpdate,
)
from common.sqlalchemy.dependencies import get_db_session


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
