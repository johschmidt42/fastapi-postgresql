from typing import TypeVar, List

from psycopg import AsyncConnection
from psycopg.abc import Query
from psycopg.rows import class_row
from pydantic import BaseModel

from app_psycopg.db.db_models import Order, OrderInput, User, UserInput, UserUpdate
from app_psycopg.db.db_statements import (
    delete_user_stmt,
    get_order_stmt,
    get_user_stmt,
    insert_order_stmt,
    insert_user_stmt,
    update_user_stmt,
    get_users_stmt,
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
            await cursor.execute(query=query, params=kwargs)
            return await cursor.fetchall()

    # User

    async def get_users(self, **kwargs) -> List[User]:
        return await self._get_resources(
            query=get_users_stmt, model_class=User, **kwargs
        )

    async def get_user(self, id: str) -> User | None:
        return await self._get_resource(query=get_user_stmt, model_class=User, id=id)

    async def insert_user(self, data: UserInput) -> str:
        return await self._insert_resource(query=insert_user_stmt, data=data)

    async def update_user(self, id: str | str, update: UserUpdate) -> str | None:
        return await self._update_resource(query=update_user_stmt, update=update, id=id)

    async def delete_user(self, id: str) -> None:
        return await self._delete_resource(delete_user_stmt, id=id)

    # Order

    async def insert_order(self, data: OrderInput) -> str:
        return await self._insert_resource(query=insert_order_stmt, data=data)

    async def get_order(self, id: str) -> Order | None:
        return await self._get_resource(query=get_order_stmt, model_class=Order, id=id)
