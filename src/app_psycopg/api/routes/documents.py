from typing import Annotated, List, Type, Optional, Set

from fastapi import APIRouter, Body, Depends, status, Query
from pydantic import AfterValidator, UUID4

from app_psycopg.api.dependencies import get_db, validate_document_id
from app_psycopg.api.models import (
    DocumentInput,
    Document,
    DocumentUpdate,
)
from app_psycopg.api.pagination import LimitOffsetPage
from app_psycopg.api.sorting import create_order_by_enum, validate_order_by_query_params
from app_psycopg.db.db import Database


router: APIRouter = APIRouter(
    tags=["Documents"],
    prefix="/documents",
)

document_sortable_fields: List[str] = ["created_at", "last_updated_at"]
OrderByDocument: Type = Annotated[
    Optional[Set[create_order_by_enum(document_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_document(
    db: Annotated[Database, Depends(get_db)],
    document_input: Annotated[DocumentInput, Body(...)],
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
    limit: Annotated[int, Query(ge=1, lt=50)] = 10,
    offset: Annotated[int, Query(ge=0, lt=1000)] = 0,
    order_by: Annotated[OrderByDocument, Query()] = None,
) -> LimitOffsetPage[Document]:
    documents: List[Document] = await db.get_documents(
        limit=limit, offset=offset, order_by=order_by
    )
    total: int = await db.get_documents_count()

    items: List[Document] = [
        Document.model_validate(document) for document in documents
    ]

    return LimitOffsetPage(
        items=items,
        items_count=len(items),
        total_count=total,
        limit=limit,
        offset=offset,
    )


@router.put(path="/{document_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_document(
    db: Annotated[Database, Depends(get_db)],
    document: Annotated[Document, Depends(validate_document_id)],
    update: Annotated[DocumentUpdate, Body(...)],
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
