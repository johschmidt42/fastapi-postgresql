import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from polyfactory.factories.pydantic_factory import ModelFactory

from app_psycopg.db.db import (
    Database,
    create_paginate_query,
)
from app_psycopg.api.models import UserInput, UserUpdate, OrderInput, User, Order


class UserFactory(ModelFactory[User]):
    __model__ = User


class OrderFactory(ModelFactory[Order]):
    __model__ = Order

    @classmethod
    def amount(cls) -> Decimal:
        return Decimal("100.00")


@pytest.mark.asyncio
async def test_create_paginate_query_from_text():
    """Test create_paginate_query_from_text function."""
    # Test with both limit and offset
    query = "SELECT * FROM users"
    result = create_paginate_query(query, 10, 5)
    # Use a more flexible assertion that ignores whitespace
    assert (
        "SELECT * FROM users" in result
        and "LIMIT 10" in result
        and "OFFSET 5" in result
    )


class AsyncCursorContextManagerMock:
    """Mock for async cursor context manager."""

    def __init__(self, cursor_mock):
        self.cursor_mock = cursor_mock

    async def __aenter__(self):
        return self.cursor_mock

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_resource():
    """Test _get_resource method."""
    # Arrange
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()
    cursor_mock.fetchone.return_value = UserFactory.build()

    # Make sure cursor() returns the context manager directly, not a coroutine
    conn_mock.cursor = MagicMock(
        return_value=AsyncCursorContextManagerMock(cursor_mock)
    )

    db = Database(conn_mock)
    query = "SELECT * FROM users WHERE id = :id"

    # Act
    result = await db._get_resource(query, User, id="test-id")

    # Assert
    assert result is not None
    conn_mock.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(query=query, params={"id": "test-id"})
    cursor_mock.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_insert_resource():
    """Test _insert_resource method."""
    # Arrange
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()
    cursor_mock.fetchone.return_value = ("test-id",)

    # Make sure cursor() returns the context manager directly, not a coroutine
    conn_mock.cursor = MagicMock(
        return_value=AsyncCursorContextManagerMock(cursor_mock)
    )

    db = Database(conn_mock)
    query = "INSERT INTO users (name) VALUES (:name) RETURNING id"
    data = UserInput(name="Test User", profession_id=uuid.uuid4())

    # Act
    result = await db._insert_resource(query, data)

    # Assert
    assert result == "test-id"
    conn_mock.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once()
    cursor_mock.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_update_resource():
    """Test _update_resource method."""
    # Arrange
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()
    cursor_mock.fetchone.return_value = ("test-id",)

    # Make sure cursor() returns the context manager directly, not a coroutine
    conn_mock.cursor = MagicMock(
        return_value=AsyncCursorContextManagerMock(cursor_mock)
    )

    db = Database(conn_mock)
    query = "UPDATE users SET name = :name WHERE id = :id RETURNING id"
    update = UserUpdate(name="Updated User", profession_id=uuid.uuid4())

    # Act
    result = await db._update_resource(query, update, id="test-id")

    # Assert
    assert result == "test-id"
    conn_mock.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once()
    cursor_mock.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_delete_resource():
    """Test _delete_resource method."""
    # Arrange
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()

    # Make sure cursor() returns the context manager directly, not a coroutine
    conn_mock.cursor = MagicMock(
        return_value=AsyncCursorContextManagerMock(cursor_mock)
    )

    db = Database(conn_mock)
    query = "DELETE FROM users WHERE id = :id"

    # Act
    result = await db._delete_resource(query, id="test-id")

    # Assert
    assert result is None
    conn_mock.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(query=query, params={"id": "test-id"})


@pytest.mark.asyncio
async def test_get_resources():
    """Test _get_resources method."""
    # Arrange
    conn_mock = AsyncMock()
    cursor_mock = AsyncMock()
    cursor_mock.fetchall.return_value = [UserFactory.build()]

    # Make sure cursor() returns the context manager directly, not a coroutine
    conn_mock.cursor = MagicMock(
        return_value=AsyncCursorContextManagerMock(cursor_mock)
    )

    db = Database(conn_mock)
    query = "SELECT * FROM users"

    # Act
    result = await db._get_resources(query, User, limit=10, offset=0)

    # Assert
    assert len(result) == 1
    conn_mock.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once()
    cursor_mock.fetchall.assert_called_once()


@pytest.mark.asyncio
async def test_get_users():
    """Test get_users method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._get_resources.return_value = [UserFactory.build()]

    # Act
    with patch("app_psycopg.db.db.Database._get_resources", db._get_resources):
        result = await Database(AsyncMock()).get_users(limit=10, offset=0)

    # Assert
    assert len(result) == 1
    db._get_resources.assert_called_once()


@pytest.mark.asyncio
async def test_get_user():
    """Test get_user method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._get_resource.return_value = UserFactory.build()

    # Act
    with patch("app_psycopg.db.db.Database._get_resource", db._get_resource):
        result = await Database(AsyncMock()).get_user(id="test-id")

    # Assert
    assert result is not None
    db._get_resource.assert_called_once()


@pytest.mark.asyncio
async def test_insert_user():
    """Test insert_user method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._insert_resource.return_value = "test-id"

    # Act
    with patch("app_psycopg.db.db.Database._insert_resource", db._insert_resource):
        result = await Database(AsyncMock()).insert_user(
            UserInput(name="Test User", profession_id=uuid.uuid4())
        )

    # Assert
    assert result == "test-id"
    db._insert_resource.assert_called_once()


@pytest.mark.asyncio
async def test_update_user():
    """Test update_user method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._update_resource.return_value = "test-id"

    # Act
    with patch("app_psycopg.db.db.Database._update_resource", db._update_resource):
        result = await Database(AsyncMock()).update_user(
            "test-id", UserUpdate(name="Updated User", profession_id=uuid.uuid4())
        )

    # Assert
    assert result == "test-id"
    db._update_resource.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user():
    """Test delete_user method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._delete_resource.return_value = None

    # Act
    with patch("app_psycopg.db.db.Database._delete_resource", db._delete_resource):
        result = await Database(AsyncMock()).delete_user("test-id")

    # Assert
    assert result is None
    db._delete_resource.assert_called_once()


@pytest.mark.asyncio
async def test_insert_order():
    """Test insert_order method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._insert_resource.return_value = "test-id"

    # Act
    with patch("app_psycopg.db.db.Database._insert_resource", db._insert_resource):
        result = await Database(AsyncMock()).insert_order(
            OrderInput(
                amount=Decimal("100.00"), payer_id=uuid.uuid4(), payee_id=uuid.uuid4()
            )
        )

    # Assert
    assert result == "test-id"
    db._insert_resource.assert_called_once()


@pytest.mark.asyncio
async def test_get_order():
    """Test get_order method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._get_resource.return_value = OrderFactory.build()

    # Act
    with patch("app_psycopg.db.db.Database._get_resource", db._get_resource):
        result = await Database(AsyncMock()).get_order(id="test-id")

    # Assert
    assert result is not None
    db._get_resource.assert_called_once()


@pytest.mark.asyncio
async def test_get_orders():
    """Test get_orders method."""
    # Arrange
    db = AsyncMock(spec=Database)
    db._get_resources.return_value = [OrderFactory.build()]

    # Act
    with patch("app_psycopg.db.db.Database._get_resources", db._get_resources):
        result = await Database(AsyncMock()).get_orders(limit=10, offset=0)

    # Assert
    assert len(result) == 1
    db._get_resources.assert_called_once()
