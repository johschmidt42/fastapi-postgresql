from typing import Annotated

from fastapi import Depends, HTTPException, Body
from pydantic import UUID4
from starlette import status

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.users import validate_user_id
from app_psycopg.db.db import Database
from common.models import (
    DocumentInput,
    DocumentUpdate,
    Document,
)


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
