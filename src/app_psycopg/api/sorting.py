from typing import List, LiteralString

from psycopg import sql
from psycopg.abc import Query

from common.sorting import OrderByField, Direction


def create_order_by_query(query: Query, order_by_fields: List[OrderByField]) -> Query:
    """
    Appends ORDER BY clauses to a SQL query based on the provided fields.

    Args:
        query (Query): The SQL query to modify (str, bytes, or psycopg.sql object).
        order_by_fields (List[OrderByField]): A list of fields to order by.

    Returns:
        Query: The modified query with ORDER BY clauses.
    """

    order_by_clauses: List[str] = [
        f"{field.name} {'ASC' if field.direction == Direction.ASC else 'DESC'} NULLS LAST"
        for field in order_by_fields
    ]

    order_by_sql: LiteralString = f" ORDER BY {', '.join(order_by_clauses)}"

    if isinstance(query, bytes):
        return query + order_by_sql.encode()
    elif isinstance(query, (sql.SQL, sql.Composed)):
        return sql.Composed([query, sql.SQL(order_by_sql)])
    elif isinstance(query, str):
        return f"{query}{order_by_sql}"
    else:
        raise TypeError(
            "Query must be a LiteralString, bytes, sql.SQL, or sql.Composed"
        )
