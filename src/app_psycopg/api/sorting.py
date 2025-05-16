from enum import StrEnum, Enum
from typing import List

from psycopg import sql
from psycopg.abc import Query
from pydantic import BaseModel


def create_order_by_options(values: List[str]) -> StrEnum:
    """
    Converts a list of strings into a StrEnum with "+" and "-" prefixes,
    providing ascending and descending options.

    Args:
        values (List[str]): A list of field names.

    Returns:
        StrEnum: An enumeration containing each field name prefixed with "+" and "-".
    """

    return StrEnum(
        value="StrEnum", names=[f"+{v}" for v in values] + [f"-{v}" for v in values]
    )


class Direction(str, Enum):
    ASC = "+"
    DESC = "-"


class OrderByField(BaseModel):
    name: str
    direction: Direction


def _parse_str_order_by(name: str) -> OrderByField:
    return OrderByField(name=name[1:], direction=Direction(name[0]))


def parse_order_by(order_by: List[str]) -> List[OrderByField]:
    return [_parse_str_order_by(ob) for ob in order_by] if order_by else None


def create_order_by_query(query: Query, order_by_fields: List[OrderByField]) -> Query:
    # TODO: fix this
    order_by_clauses: List[sql.Composed] = [
        sql.SQL("{} {} NULLS LAST").format(
            sql.Identifier(field.name),
            sql.SQL("ASC" if field.direction == Direction.ASC else "DESC"),
        )
        for field in order_by_fields
    ]

    order_by_sql: sql.Composed = sql.SQL(" ORDER BY {}").format(
        sql.SQL(", ").join(order_by_clauses)
    )

    return f"{query} {order_by_sql.as_string()}"
