import pytest
from psycopg import sql
from app_psycopg.api.pagination import LimitOffsetPage, create_paginate_query


def test_limit_offset_page():
    """Test LimitOffsetPage model."""
    # Test with valid data
    page = LimitOffsetPage(
        items=["item1", "item2"],
        items_count=2,
        total_count=10,
        limit=5,
        offset=0,
    )
    assert page.items == ["item1", "item2"]
    assert page.items_count == 2
    assert page.total_count == 10
    assert page.limit == 5
    assert page.offset == 0

    # Test with empty items
    page = LimitOffsetPage(
        items=[],
        items_count=0,
        total_count=10,
        limit=5,
        offset=0,
    )
    assert page.items == []
    assert page.items_count == 0


def test_create_paginate_query_with_string():
    """Test create_paginate_query with string input."""
    query = "SELECT * FROM users"
    result = create_paginate_query(query, 10, 5)
    assert result == "SELECT * FROM users LIMIT 10 OFFSET 5"


def test_create_paginate_query_with_bytes():
    """Test create_paginate_query with bytes input."""
    query = b"SELECT * FROM users"
    result = create_paginate_query(query, 10, 5)
    assert result == b"SELECT * FROM users LIMIT 10 OFFSET 5"


def test_create_paginate_query_with_sql():
    """Test create_paginate_query with sql.SQL input."""
    query = sql.SQL("SELECT * FROM users")
    result = create_paginate_query(query, 10, 5)
    # Convert result to string for comparison
    assert result.as_string(None) == "SELECT * FROM users LIMIT 10 OFFSET 5"


def test_create_paginate_query_with_composed():
    """Test create_paginate_query with sql.Composed input."""
    query = sql.Composed([sql.SQL("SELECT * FROM users")])
    result = create_paginate_query(query, 10, 5)
    # Convert result to string for comparison
    assert result.as_string(None) == "SELECT * FROM users LIMIT 10 OFFSET 5"


def test_create_paginate_query_invalid_type():
    """Test create_paginate_query with invalid input type."""
    query = 123  # Invalid type
    with pytest.raises(TypeError) as exc_info:
        create_paginate_query(query, 10, 5)
    assert "Query must be a LiteralString, bytes, sql.SQL, or sql.Composed" in str(
        exc_info.value
    )
