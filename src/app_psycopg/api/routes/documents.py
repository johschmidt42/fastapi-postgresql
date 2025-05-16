from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, status, Query

from app_psycopg.api.dependencies import get_db, validate_document_id
from app_psycopg.api.models import (
    DocumentInput,
    DocumentResponseModel,
    DocumentUpdate,
)
from app_psycopg.api.pagination import LimitOffsetPage
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import Document

router: APIRouter = APIRouter(
    tags=["Documents"],
    prefix="/documents",
)


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_document(
    db: Annotated[Database, Depends(get_db)],
    document_input: Annotated[DocumentInput, Body(...)],
) -> str:
    document_id: str = await db.insert_document(document_input)
    return document_id


@router.get(
    path="/{document_id}",
    response_model=DocumentResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document: Annotated[Document, Depends(validate_document_id)],
) -> DocumentResponseModel:
    return DocumentResponseModel.model_validate(document)


@router.get(
    path="",
    response_model=LimitOffsetPage[DocumentResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_documents(
    db: Annotated[Database, Depends(get_db)],
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
) -> LimitOffsetPage[DocumentResponseModel]:
    documents: List[Document] = await db.get_documents(limit=limit, offset=offset)
    total: int = await db.get_documents_count() if documents else 0

    items: List[DocumentResponseModel] = [
        DocumentResponseModel.model_validate(document) for document in documents
    ]

    return LimitOffsetPage(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.put(path="/{document_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_document(
    db: Annotated[Database, Depends(get_db)],
    document: Annotated[Document, Depends(validate_document_id)],
    update: Annotated[DocumentUpdate, Body(...)],
) -> str:
    document_id: str = await db.update_document(id=document.id, update=update)
    return document_id


@router.delete(
    path="/{document_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(
    db: Annotated[Database, Depends(get_db)],
    document: Annotated[Document, Depends(validate_document_id)],
) -> None:
    await db.delete_document(document.id)
