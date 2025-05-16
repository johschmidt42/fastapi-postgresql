from typing import Generic, TypeVar, Sequence, List

from psycopg.abc import Query
from pydantic import conint
from pydantic.v1.generics import GenericModel
from psycopg import sql


DataT: TypeVar = TypeVar("DataT")


class LimitOffsetPage(GenericModel, Generic[DataT]):
    items: Sequence[DataT]
    total: conint(ge=0)
    limit: conint(ge=1)
    offset: conint(ge=0)


def create_paginate_query(query: Query, limit: int, offset: int) -> Query:
    suffix_parts: List[sql.Composed] = [
        sql.SQL("LIMIT {}").format(sql.Literal(limit)),
        sql.SQL("OFFSET {}").format(sql.Literal(offset)),
    ]

    suffix: sql.Composed = sql.Composed(suffix_parts)

    if isinstance(query, bytes):
        return query + bytes(str(suffix), "utf-8")
    elif isinstance(query, sql.SQL) or isinstance(query, sql.Composed):
        return sql.Composed([query, sql.SQL(" "), suffix])
    else:
        return f"{query} {suffix}".strip()
