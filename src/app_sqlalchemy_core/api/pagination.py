from typing import Generic, TypeVar, Sequence

from pydantic import conint, BaseModel, Field
from sqlalchemy import Select

DataT: TypeVar = TypeVar("DataT")


class LimitOffsetPage(BaseModel, Generic[DataT]):
    items: Sequence[DataT]
    items_count: conint(ge=0)
    total_count: conint(ge=0)
    limit: conint(ge=1, le=50)
    offset: conint(ge=0, le=1000)


class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=50)
    offset: int = Field(0, ge=0, le=1000)


def create_paginate_query(query: Select, limit: int, offset: int) -> Select:
    """
    Applies LIMIT and OFFSET clauses to a SQLAlchemy Select query.

    Args:
        query: The SQLAlchemy Select statement object.
        limit: The maximum number of rows to return (LIMIT).
        offset: The number of rows to skip before starting to return rows (OFFSET).

    Returns:
        A new SQLAlchemy Select statement object with LIMIT and OFFSET applied.
    """

    # Apply limit and offset to the query
    paginated_query: Select = query.limit(limit).offset(offset)

    return paginated_query
