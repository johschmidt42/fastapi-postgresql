from typing import TypeVar, List, cast

from psycopg import AsyncConnection
from psycopg.abc import Query
from psycopg.rows import class_row
from pydantic import BaseModel

from app_psycopg.api.models import (
    UserInput,
    UserUpdate,
    OrderInput,
    DocumentInput,
    DocumentUpdate,
)
from app_psycopg.api.pagination import create_paginate_query_from_text
from app_psycopg.db.db_models import Order, User, Document
from app_psycopg.db.db_statements import (
    delete_user_stmt,
    get_order_stmt,
    get_user_stmt,
    insert_order_stmt,
    insert_user_stmt,
    update_user_stmt,
    get_users_stmt,
    get_users_count_stmt,
    get_orders_stmt,
    get_document_stmt,
    get_documents_stmt,
    insert_document_stmt,
    document_user_stmt,
    delete_document_stmt,
    get_documents_count_stmt,
)

T: TypeVar = TypeVar("T")


class Database:
    def __init__(self, connection: AsyncConnection):
        self.conn: AsyncConnection = connection

    async def _get_resource(
        self, query: Query, model_class: type[T], **kwargs
    ) -> T | None:
        async with self.conn.cursor(row_factory=class_row(cls=model_class)) as cursor:
            await cursor.execute(query=query, params=kwargs)
            return await cursor.fetchone()

    async def _insert_resource(self, query: Query, data: BaseModel) -> str:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=data.model_dump())
            data_out: tuple = await cursor.fetchone()
            return data_out[0]

    async def _update_resource(
        self, query: Query, update: BaseModel, **kwargs
    ) -> str | None:
        async with self.conn.cursor() as cursor:
            kwargs.update(update.model_dump())
            await cursor.execute(query=query, params=kwargs)
            data_out: tuple = await cursor.fetchone()
            return data_out[0]

    async def _delete_resource(self, query: Query, **kwargs) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=kwargs)

    async def _get_resources(
        self, query: Query, model_class: type[T], **kwargs
    ) -> List[T]:
        async with self.conn.cursor(row_factory=class_row(cls=model_class)) as cursor:
            await cursor.execute(
                query=create_paginate_query_from_text(
                    query=query, limit=kwargs.get("limit"), offset=kwargs.get("offset")
                ),
                params=kwargs,
            )
            return await cursor.fetchall()

    async def _get_count(self, query: Query) -> int:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query)
            result = await cursor.fetchone()
            return cast(int, result[0])

    # User

    async def get_users(self, **kwargs) -> List[User]:
        return await self._get_resources(
            query=get_users_stmt, model_class=User, **kwargs
        )

    async def get_users_count(self) -> int:
        return await self._get_count(query=get_users_count_stmt)

    async def get_user(self, id: str) -> User | None:
        return await self._get_resource(query=get_user_stmt, model_class=User, id=id)

    async def insert_user(self, data: UserInput) -> str:
        return await self._insert_resource(query=insert_user_stmt, data=data)

    async def update_user(self, id: str, update: UserUpdate) -> str | None:
        return await self._update_resource(query=update_user_stmt, update=update, id=id)

    async def delete_user(self, id: str) -> None:
        return await self._delete_resource(delete_user_stmt, id=id)

    # Order

    async def insert_order(self, data: OrderInput) -> str:
        return await self._insert_resource(query=insert_order_stmt, data=data)

    async def get_order(self, id: str) -> Order | None:
        return await self._get_resource(query=get_order_stmt, model_class=Order, id=id)

    async def get_orders(self, **kwargs) -> List[Order]:
        return await self._get_resources(
            query=get_orders_stmt, model_class=Order, **kwargs
        )

    # Documents

    async def insert_document(self, data: DocumentInput) -> str:
        return await self._insert_resource(query=insert_document_stmt, data=data)

    async def update_document(self, id: str, update: DocumentUpdate) -> str | None:
        return await self._update_resource(
            query=document_user_stmt, update=update, id=id
        )

    async def get_document(self, id: str) -> Document | None:
        return await self._get_resource(
            query=get_document_stmt, model_class=Document, id=id
        )

    async def get_documents(self, **kwargs) -> List[Document]:
        return await self._get_resources(
            query=get_documents_stmt, model_class=Document, **kwargs
        )

    async def get_documents_count(self) -> int:
        return await self._get_count(query=get_documents_count_stmt)

    async def delete_document(self, id: str) -> None:
        return await self._delete_resource(delete_document_stmt, id=id)
