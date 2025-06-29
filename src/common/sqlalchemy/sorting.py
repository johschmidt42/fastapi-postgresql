from typing import List, Any

from sqlalchemy import Select, asc, desc, nulls_last

from common.sorting import OrderByField, Direction


def create_order_by_query(
    query: Select, order_by_fields: List[OrderByField], model: Any
) -> Select:
    """
    Adds ORDER BY clauses to a SQLAlchemy query based on the provided order_by fields.

    Args:
        query (Select): The SQLAlchemy query to modify.
        order_by_fields (List[OrderByField]): A list of fields to order by.
        model (Any): The SQLAlchemy model class.

    Returns:
        Select: The modified query with ORDER BY clauses.
    """
    if not order_by_fields:
        return query

    # grab the ColumnCollection
    # ORM class:   model.__table__ -> Table -> .c
    # Core Table:  model           -> .c
    tbl = getattr(model, "__table__", model)
    cols = getattr(tbl, "c", tbl)

    order_clauses = []
    for field in order_by_fields:
        col = getattr(cols, field.name)
        if field.direction is Direction.ASC:
            order_clauses.append(nulls_last(asc(col)))
        else:
            order_clauses.append(nulls_last(desc(col)))

    return query.order_by(*order_clauses)
