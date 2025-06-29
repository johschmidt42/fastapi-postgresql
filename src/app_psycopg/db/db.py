from typing import TypeVar, List, cast, Tuple

from psycopg import AsyncConnection
from psycopg.abc import Query
from psycopg.rows import class_row
from pydantic import BaseModel, UUID4

from common.models import (
    UserInput,
    UserUpdate,
    OrderInput,
    DocumentInput,
    DocumentUpdate,
    ProfessionInput,
    ProfessionUpdate,
    User,
    Order,
    Document,
    Profession,
    UserPatch,
    CompanyInput,
    CompanyUpdate,
    Company,
    CompanyPatch,
    UserCompanyLinkInput,
    UserCompanyLinkWithCompany,
    UserCompanyLinkWithUser,
    UserCompanyLink,
)
from app_psycopg.api.pagination import create_paginate_query
from app_psycopg.api.sorting import create_order_by_query

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
    get_orders_count_stmt,
    insert_profession_stmt,
    get_profession_stmt,
    get_professions_stmt,
    get_professions_count_stmt,
    update_profession_stmt,
    delete_profession_stmt,
    patch_user_stmt,
    delete_order_stmt,
    insert_company_stmt,
    get_company_stmt,
    get_companies_stmt,
    get_companies_count_stmt,
    update_company_stmt,
    patch_company_stmt,
    delete_company_stmt,
    insert_user_company_link_stmt,
    get_user_company_links_by_user_stmt,
    get_user_company_links_by_company_stmt,
    get_user_company_links_count_by_user_stmt,
    get_user_company_links_count_by_company_stmt,
    delete_user_company_link_stmt,
    get_user_company_link_stmt,
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

    async def _insert_resource(self, query: Query, data: BaseModel) -> UUID4 | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=data.model_dump())
            data_out: tuple = await cursor.fetchone()
            return data_out[0] if data_out else None

    async def _insert_joint_resource(
        self, query: Query, data: BaseModel
    ) -> Tuple[UUID4, UUID4] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=data.model_dump())
            data_out: tuple = await cursor.fetchone()

            return data_out if data_out else None

    async def _update_resource(
        self, query: Query, update: BaseModel, **kwargs
    ) -> UUID4:
        async with self.conn.cursor() as cursor:
            kwargs.update(update.model_dump())
            await cursor.execute(query=query, params=kwargs)
            data_out: tuple = await cursor.fetchone()
            return data_out[0]

    async def _patch_resource(self, query: Query, patch: BaseModel, **kwargs) -> UUID4:
        async with self.conn.cursor() as cursor:
            kwargs.update(patch.model_dump())
            await cursor.execute(query=query, params=kwargs)
            data_out: tuple = await cursor.fetchone()
            return data_out[0]

    async def _delete_resource(self, query: Query, **kwargs) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=kwargs)

    async def _get_resources(
        self, query: Query, model_class: type[T], **kwargs
    ) -> List[T]:
        if kwargs.get("order_by") is not None:
            query: Query = create_order_by_query(
                query=query, order_by_fields=kwargs.get("order_by")
            )

        if kwargs.get("limit") is not None and kwargs.get("offset") is not None:
            query: Query = create_paginate_query(
                query=query, limit=kwargs["limit"], offset=kwargs["offset"]
            )

        async with self.conn.cursor(row_factory=class_row(cls=model_class)) as cursor:
            await cursor.execute(
                query=query,
                params=kwargs,
            )
            return await cursor.fetchall()

    async def _get_count(self, query: Query, **kwargs) -> int:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query=query, params=kwargs)
            result = await cursor.fetchone()
            return cast(int, result[0])

    # User

    async def get_users(self, **kwargs) -> List[User]:
        query: Query = get_users_stmt

        return await self._get_resources(query=query, model_class=User, **kwargs)

    async def get_users_count(self) -> int:
        return await self._get_count(query=get_users_count_stmt)

    async def get_user(self, id: str) -> User | None:
        return await self._get_resource(query=get_user_stmt, model_class=User, id=id)

    async def insert_user(self, data: UserInput) -> UUID4 | None:
        return await self._insert_resource(query=insert_user_stmt, data=data)

    async def update_user(self, id: str, update: UserUpdate) -> UUID4:
        return await self._update_resource(query=update_user_stmt, update=update, id=id)

    async def patch_user(self, id: str, patch: UserPatch) -> UUID4:
        return await self._patch_resource(query=patch_user_stmt, patch=patch, id=id)

    async def delete_user(self, id: str) -> None:
        return await self._delete_resource(delete_user_stmt, id=id)

    # Order

    async def insert_order(self, data: OrderInput) -> UUID4 | None:
        return await self._insert_resource(query=insert_order_stmt, data=data)

    async def get_order(self, id: str) -> Order | None:
        return await self._get_resource(query=get_order_stmt, model_class=Order, id=id)

    async def get_orders(self, **kwargs) -> List[Order]:
        query: Query = get_orders_stmt

        return await self._get_resources(query=query, model_class=Order, **kwargs)

    async def get_orders_count(self) -> int:
        return await self._get_count(query=get_orders_count_stmt)

    async def delete_order(self, id: str) -> None:
        return await self._delete_resource(delete_order_stmt, id=id)

    # Documents

    async def insert_document(self, data: DocumentInput) -> UUID4 | None:
        return await self._insert_resource(query=insert_document_stmt, data=data)

    async def update_document(self, id: str, update: DocumentUpdate) -> UUID4:
        return await self._update_resource(
            query=document_user_stmt, update=update, id=id
        )

    async def get_document(self, id: str) -> Document | None:
        return await self._get_resource(
            query=get_document_stmt, model_class=Document, id=id
        )

    async def get_documents(self, **kwargs) -> List[Document]:
        query: Query = get_documents_stmt

        return await self._get_resources(query=query, model_class=Document, **kwargs)

    async def get_documents_count(self) -> int:
        return await self._get_count(query=get_documents_count_stmt)

    async def delete_document(self, id: str) -> None:
        return await self._delete_resource(delete_document_stmt, id=id)

    # Profession

    async def get_professions(self, **kwargs) -> List[Profession]:
        query: Query = get_professions_stmt

        return await self._get_resources(query=query, model_class=Profession, **kwargs)

    async def get_professions_count(self) -> int:
        return await self._get_count(query=get_professions_count_stmt)

    async def get_profession(self, id: str) -> Profession | None:
        return await self._get_resource(
            query=get_profession_stmt, model_class=Profession, id=id
        )

    async def insert_profession(self, data: ProfessionInput) -> UUID4 | None:
        return await self._insert_resource(query=insert_profession_stmt, data=data)

    async def update_profession(self, id: str, update: ProfessionUpdate) -> UUID4:
        return await self._update_resource(
            query=update_profession_stmt, update=update, id=id
        )

    async def delete_profession(self, id: str) -> None:
        return await self._delete_resource(delete_profession_stmt, id=id)

    # Company

    async def get_companies(self, **kwargs) -> List[Company]:
        query: Query = get_companies_stmt

        return await self._get_resources(query=query, model_class=Company, **kwargs)

    async def get_companies_count(self) -> int:
        return await self._get_count(query=get_companies_count_stmt)

    async def get_company(self, id: str) -> Company | None:
        return await self._get_resource(
            query=get_company_stmt, model_class=Company, id=id
        )

    async def insert_company(self, data: CompanyInput) -> UUID4 | None:
        return await self._insert_resource(query=insert_company_stmt, data=data)

    async def update_company(self, id: str, update: CompanyUpdate) -> UUID4:
        return await self._update_resource(
            query=update_company_stmt, update=update, id=id
        )

    async def patch_company(self, id: str, patch: CompanyPatch) -> UUID4:
        return await self._patch_resource(query=patch_company_stmt, patch=patch, id=id)

    async def delete_company(self, id: str) -> None:
        return await self._delete_resource(delete_company_stmt, id=id)

    # UserCompanyLink

    async def get_user_company_link(
        self, user_id: UUID4, company_id: UUID4
    ) -> UserCompanyLink:
        return await self._get_resource(
            query=get_user_company_link_stmt,
            user_id=user_id,
            company_id=company_id,
            model_class=UserCompanyLink,
        )

    async def insert_user_company_link(
        self, data: UserCompanyLinkInput
    ) -> Tuple[UUID4, UUID4] | None:
        return await self._insert_joint_resource(
            query=insert_user_company_link_stmt, data=data
        )

    async def get_user_company_links_by_user(
        self, user_id: UUID4, **kwargs
    ) -> List[UserCompanyLinkWithCompany]:
        query: Query = get_user_company_links_by_user_stmt

        kwargs["user_id"] = user_id

        return await self._get_resources(
            query=query, model_class=UserCompanyLinkWithCompany, **kwargs
        )

    async def get_user_company_links_by_company(
        self, company_id: str, **kwargs
    ) -> List[UserCompanyLinkWithUser]:
        query: Query = get_user_company_links_by_company_stmt

        kwargs["company_id"] = company_id

        return await self._get_resources(
            query=query, model_class=UserCompanyLinkWithUser, **kwargs
        )

    async def get_user_company_links_count_by_user(self, user_id: str) -> int:
        return await self._get_count(
            query=get_user_company_links_count_by_user_stmt, user_id=user_id
        )

    async def get_user_company_links_count_by_company(self, company_id: str) -> int:
        return await self._get_count(
            query=get_user_company_links_count_by_company_stmt, company_id=company_id
        )

    async def delete_user_company_link(self, user_id: str, company_id: str) -> None:
        return await self._delete_resource(
            query=delete_user_company_link_stmt, user_id=user_id, company_id=company_id
        )
