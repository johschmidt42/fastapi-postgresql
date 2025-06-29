from sqlalchemy import Select


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
