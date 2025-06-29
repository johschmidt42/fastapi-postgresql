from typing import Any, Dict, Sequence
from sqlalchemy import and_, not_
from sqlalchemy import Select


def apply_filters(query: Select, filters: Dict[str, Any], model: Any) -> Select:
    """
    Apply a set of dynamic filters to a SQLAlchemy Core Select query.

    Supported operators (suffix after "__"):
      • eq           → equals
      • not_eq       → not equals
      • lt           → less than
      • lte          → less than or equal
      • gt           → greater than
      • gte          → greater than or equal
      • in_          → IN list
      • not_in       → NOT IN list
      • between      → BETWEEN two values (pass a 2-element Sequence)
      • not_between  → NOT BETWEEN two values (2-element Sequence)
      • like         → raw SQL LIKE (you must include “%” if needed)
      • not_like     → negated raw SQL LIKE
      • contains     → substring match (uses LIKE %value%)
      • icontains    → case-insensitive substring (ILIKE %value%)
      • startswith   → LIKE value%
      • endswith     → LIKE %value%

    Args:
        query (Select):       The base SQLAlchemy Core Select query.
        filters (dict):       Mapping of filter expressions to values.
                              Keys are "<column>__<op>", e.g.
                                {"age__gte": 18,
                                 "name__icontains": "smith",
                                 "tags__in_": ["red","blue"]}
        model (Table|Alias):  SQLAlchemy Table (or selectable) with `.c` columns.

    Returns:
        Select: The modified query with `.where(...)` clauses applied.

    Example:
        from sqlalchemy import select
        from myapp.db import users_table

        raw_filters = {
            "age__gte": 21,
            "status__not_eq": "deleted",
            "country__in_": ["US", "DE", "FR"],
            "username__icontains": "jon",
            "score__between": [10, 50],
        }
        q = select(users_table)
        q = apply_filters(q, raw_filters, users_table)
    """
    conditions = []
    for field_op, value in filters.items():
        if value is None:
            continue

        if "__" in field_op:
            field, op = field_op.split("__", 1)
        else:
            field, op = field_op, "eq"

        column = getattr(model.c, field, None)
        if column is None:
            continue

        # Equality / comparison
        if op == "eq":
            conditions.append(column == value)
        elif op == "not_eq":
            conditions.append(column != value)
        elif op == "lt":
            conditions.append(column < value)
        elif op == "lte":
            conditions.append(column <= value)
        elif op == "gt":
            conditions.append(column > value)
        elif op == "gte":
            conditions.append(column >= value)

        # IN / NOT IN
        elif op == "in_" and isinstance(value, Sequence):
            conditions.append(column.in_(value))
        elif op == "not_in" and isinstance(value, Sequence):
            conditions.append(column.notin_(value))

        # BETWEEN / NOT BETWEEN
        elif op == "between" and isinstance(value, Sequence) and len(value) == 2:
            conditions.append(column.between(value[0], value[1]))
        elif op == "not_between" and isinstance(value, Sequence) and len(value) == 2:
            conditions.append(not_(column.between(value[0], value[1])))

        # LIKE / ILIKE / CONTAINS
        elif op == "like":
            conditions.append(column.like(value))
        elif op == "not_like":
            conditions.append(not_(column.like(value)))
        elif op == "contains":
            conditions.append(column.contains(value))
        elif op == "icontains":
            conditions.append(column.ilike(f"%{value}%"))
        elif op == "ilike":
            conditions.append(column.ilike(value))

        # STARTSWITH / ENDSWITH
        elif op == "startswith":
            conditions.append(column.startswith(value))
        elif op == "endswith":
            conditions.append(column.endswith(value))

    if conditions:
        query = query.where(and_(*conditions))

    return query
