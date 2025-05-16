from typing import Generic, TypeVar, Sequence

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


def create_paginate_query_from_text(query: Query, limit: int, offset: int) -> Query:
    suffix_parts = [
        sql.SQL("LIMIT {}").format(sql.Literal(limit)),
        sql.SQL("OFFSET {}").format(sql.Literal(offset)),
    ]

    suffix: sql.Composed = sql.Composed(suffix_parts)

    if isinstance(query, bytes):
        return query + bytes(str(suffix), "utf-8")
    elif isinstance(query, sql.SQL) or isinstance(query, sql.Composed):
        return sql.Composed([query, sql.SQL(" "), suffix])
    else:  # Assuming the fallback is a string (LiteralString)
        return f"{query} {suffix}".strip()
