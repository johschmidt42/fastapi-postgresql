from typing import Generic, TypeVar, Sequence, LiteralString

from psycopg.abc import Query
from pydantic import conint, BaseModel

from psycopg import sql


DataT: TypeVar = TypeVar("DataT")


class LimitOffsetPage(BaseModel, Generic[DataT]):
    items: Sequence[DataT]
    items_count: conint(ge=0)
    total_count: conint(ge=0)
    limit: conint(ge=1)
    offset: conint(ge=0)


def create_paginate_query(query: Query, limit: int, offset: int) -> Query:
    suffix: LiteralString = f" LIMIT {limit} OFFSET {offset}"

    if isinstance(query, bytes):
        return query + suffix.encode()
    elif isinstance(query, (sql.SQL, sql.Composed)):
        return sql.Composed([query, sql.SQL(suffix)])
    elif isinstance(query, str):
        return f"{query}{suffix}"
    else:
        raise TypeError(
            "Query must be a LiteralString, bytes, sql.SQL, or sql.Composed"
        )
