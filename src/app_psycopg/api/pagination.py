from typing import LiteralString

from psycopg import sql
from psycopg.abc import Query


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
