from typing import Annotated, List, Any

from app_sqlalchemy_core.api.models import Document as DocumentResponseModel
from app_sqlalchemy_core.api.pagination import PaginationParams, create_paginate_query
from app_sqlalchemy_core.api.sorting import (
    create_order_by_query,
)
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import Select, Result, Sequence, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlalchemy_core.api.dependencies import (
    validate_document_id,
    get_db_session,
    validate_document_input,
    validate_document_update,
)
from app_sqlalchemy_core.db.models import Document
from common.order_by_enums import OrderByDocument
from common.schemas import (
    DocumentInput,
    DocumentUpdate,
)

router: APIRouter = APIRouter(
    tags=["Documents"],
    prefix="/documents",
)


@router.post(path="", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_document(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    document_input: Annotated[DocumentInput, Depends(validate_document_input)],
) -> str:
    new_document: Document = Document(
        id=document_input.id,
        document=document_input.document,
        created_at=document_input.created_at,
    )

    db_session.add(new_document)

    return new_document.id


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
    path="", response_model=List[DocumentResponseModel], status_code=status.HTTP_200_OK
)
async def get_documents(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends()],
    order_by: Annotated[OrderByDocument, Query()] = None,
) -> List[DocumentResponseModel]:
    query: Select = create_paginate_query(
        query=select(Document), limit=pagination.limit, offset=pagination.offset
    )

    if order_by:
        query: Select = create_order_by_query(
            query=query, order_by_fields=order_by, model=Document
        )

    result: Result = await db_session.execute(query)

    documents: Sequence[Row | RowMapping | Any] = result.scalars().all()

    return [DocumentResponseModel.model_validate(document) for document in documents]


@router.put(path="/{document_id}", response_model=str, status_code=status.HTTP_200_OK)
async def update_document(
    document: Annotated[Document, Depends(validate_document_id)],
    update: Annotated[DocumentUpdate, Depends(validate_document_update)],
) -> str:
    document.document = update.document
    document.last_updated_at = update.last_updated_at

    return document.id


@router.delete(
    path="/{document_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    document: Annotated[Document, Depends(validate_document_id)],
) -> None:
    await db_session.delete(document)
