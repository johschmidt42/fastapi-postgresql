import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, Request
from psycopg import Connection, AsyncConnection

from app_psycopg.api.dependencies import (
    validate_document_id,
    validate_user_id,
    get_conn,
    get_db,
    validate_order_input,
    ValidatedOrder,
)
from app_psycopg.db.db import Database
from app_psycopg.api.models import OrderInput, Document, User, Profession
from polyfactory.factories.pydantic_factory import ModelFactory


class DocumentFactory(ModelFactory[Document]):
    __model__ = Document

    @classmethod
    def document(cls) -> dict:
        return {"key": "value"}


class ProfessionFactory(ModelFactory[Profession]):
    __model__ = Profession


class UserFactory(ModelFactory[User]):
    __model__ = User

    @classmethod
    def profession(cls) -> Profession:
        return ProfessionFactory.build()


class AsyncContextManagerMock:
    """Mock for async context managers."""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_conn():
    """Test get_conn."""
    # Arrange
    mock_connection = AsyncMock(spec=Connection)
    mock_conn_pool = MagicMock()
    mock_conn_pool.connection.return_value = AsyncContextManagerMock(mock_connection)

    mock_request = MagicMock(spec=Request)
    mock_request.state.conn_pool = mock_conn_pool

    # Act
    conn_generator = get_conn(mock_request)
    conn = await conn_generator.__anext__()

    # Assert
    assert conn == mock_connection
    mock_conn_pool.connection.assert_called_once()


@pytest.mark.asyncio
async def test_get_db():
    """Test get_db."""
    # Arrange
    mock_conn = MagicMock(spec=AsyncConnection)

    # Act
    db = await get_db(mock_conn)

    # Assert
    assert isinstance(db, Database)
    assert db.conn == mock_conn


@pytest.mark.asyncio
async def test_validate_document_id_success():
    """Test validate_document_id when document exists."""
    # Arrange
    document_id = uuid.uuid4()
    document = DocumentFactory.build(id=document_id)

    mock_db = AsyncMock()
    mock_db.get_document.return_value = document

    # Act
    result = await validate_document_id(db=mock_db, document_id=document_id)

    # Assert
    assert result == document
    mock_db.get_document.assert_called_once_with(document_id)


@pytest.mark.asyncio
async def test_validate_document_id_not_found():
    """Test validate_document_id when document does not exist."""
    # Arrange
    document_id = "non-existent-document-id"

    mock_db = AsyncMock()
    mock_db.get_document.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await validate_document_id(db=mock_db, document_id=document_id)

    assert exc_info.value.status_code == 404
    assert f"Document '{document_id}' not found!" in exc_info.value.detail
    mock_db.get_document.assert_called_once_with(document_id)


@pytest.mark.asyncio
async def test_validate_user_id_success():
    """Test validate_user_id when user exists."""
    # Arrange
    user_id = uuid.uuid4()
    user = UserFactory.build(id=user_id)

    mock_db = AsyncMock()
    mock_db.get_user.return_value = user

    # Act
    result = await validate_user_id(db=mock_db, user_id=user_id)

    # Assert
    assert result == user
    mock_db.get_user.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_validate_user_id_not_found():
    """Test validate_user_id when user does not exist."""
    # Arrange
    user_id = "non-existent-user-id"

    mock_db = AsyncMock()
    mock_db.get_user.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await validate_user_id(db=mock_db, user_id=user_id)

    assert exc_info.value.status_code == 404
    assert f"User '{user_id}' not found!" in exc_info.value.detail
    mock_db.get_user.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_validate_order_input_success():
    """Test validate_order_input when both payer and payee exist."""
    # Arrange
    payer_id = uuid.uuid4()
    payee_id = uuid.uuid4()
    payer = UserFactory.build(id=payer_id)
    payee = UserFactory.build(id=payee_id)
    order_input = OrderInput(
        amount=Decimal("100.00"), payer_id=payer_id, payee_id=payee_id
    )

    mock_db = AsyncMock()

    # Mock validate_user_id to return the users
    with patch("app_psycopg.api.dependencies.validate_user_id") as mock_validate:
        mock_validate.side_effect = [payer, payee]

        # Act
        result = await validate_order_input(db=mock_db, order_input=order_input)

        # Assert
        assert isinstance(result, ValidatedOrder)
        assert result.order_input == order_input
        assert result.payer == payer
        assert result.payee == payee
        assert mock_validate.call_count == 2
        mock_validate.assert_any_call(db=mock_db, user_id=payer_id)
        mock_validate.assert_any_call(db=mock_db, user_id=payee_id)
