from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from pydantic import UUID4

from app_psycopg.api.dependencies.db import get_db
from app_psycopg.api.dependencies.documents import (
    validate_document_input,
    validate_document_id,
    validate_document_update,
)
from app_psycopg.db.db import Database
from common.order_by_enums import OrderByDocument
from common.pagination import LimitOffsetPage, PaginationParams
from common.schemas import (
    DocumentInput,
    Document,
    DocumentUpdate,
)

router: APIRouter = APIRouter(
    tags=["Documents"],
    prefix="/documents",
)


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_document(
    db: Annotated[Database, Depends(get_db)],
    document_input: Annotated[DocumentInput, Depends(validate_document_input)],
) -> str:
    document_id: UUID4 = await db.insert_document(document_input)
    return document_id


@router.get(
    path="/{document_id}",
    response_model=Document,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document: Annotated[Document, Depends(validate_document_id)],
) -> Document:
    return Document.model_validate(document)


@router.get(
    path="",
    response_model=LimitOffsetPage[Document],
    status_code=status.HTTP_200_OK,
)
async def get_documents(
    db: Annotated[Database, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByDocument, Query()] = None,
) -> LimitOffsetPage[Document]:
    documents: List[Document] = await db.get_documents(
        limit=pagination.limit, offset=pagination.offset, order_by=order_by
    )
    total: int = await db.get_documents_count()

    items: List[Document] = [
        Document.model_validate(document) for document in documents
    ]

    return LimitOffsetPage(
        items=items,
        items_count=len(items),
        total_count=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.put(path="/{document_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_document(
    db: Annotated[Database, Depends(get_db)],
    document: Annotated[Document, Depends(validate_document_id)],
    update: Annotated[DocumentUpdate, Depends(validate_document_update)],
) -> str:
    document_id: UUID4 = await db.update_document(id=document.id, update=update)
    return document_id


@router.delete(
    path="/{document_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(
    db: Annotated[Database, Depends(get_db)],
    document: Annotated[Document, Depends(validate_document_id)],
) -> None:
    await db.delete_document(document.id)
