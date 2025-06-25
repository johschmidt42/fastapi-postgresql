import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection

from app_sqlalchemy_orm.api.dependencies import (
    get_db_connection,
    get_db_session,
    validate_user_id,
    validate_order_input,
    validate_document_id,
    ValidatedOrder,
)
from app_sqlalchemy_orm.api.models import OrderInput
from app_sqlalchemy_orm.db.db_models import User, Document
from tests.app_sqlalchemy.conftest import UserFactory, DocumentFactory


class AsyncContextManagerMock:
    """Mock for async context managers."""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_db_connection():
    """Test get_db_connection."""
    # Arrange
    mock_connection = AsyncMock(spec=AsyncConnection)
    mock_engine = MagicMock()
    mock_engine.begin.return_value = AsyncContextManagerMock(mock_connection)

    mock_conn_pool = MagicMock()
    mock_conn_pool._engine = mock_engine

    mock_request = MagicMock(spec=Request)
    mock_request.state.conn_pool = mock_conn_pool

    # Act
    connection_generator = get_db_connection(mock_request)
    connection = await connection_generator.__anext__()

    # Assert
    assert connection == mock_connection
    mock_engine.begin.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_session():
    """Test get_db_session."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.begin.return_value = AsyncContextManagerMock(None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = AsyncContextManagerMock(mock_session)

    mock_conn_pool = MagicMock()
    mock_conn_pool._sessionmaker = mock_sessionmaker

    mock_request = MagicMock(spec=Request)
    mock_request.state.conn_pool = mock_conn_pool

    # Act
    session_generator = get_db_session(mock_request)
    session = await session_generator.__anext__()

    # Assert
    assert session == mock_session
    mock_sessionmaker.assert_called_once()
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
async def test_validate_user_id_success():
    """Test validate_user_id when user exists."""
    # Arrange
    session = AsyncMock()
    user_id = "test-user-id"
    user = UserFactory.build(id=user_id)
    session.get.return_value = user

    # Act
    result = await validate_user_id(session=session, user_id=user_id)

    # Assert
    assert result == user
    session.get.assert_called_once_with(User, user_id)


@pytest.mark.asyncio
async def test_validate_user_id_not_found():
    """Test validate_user_id when user does not exist."""
    # Arrange
    session = AsyncMock()
    user_id = "non-existent-user-id"
    session.get.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await validate_user_id(session=session, user_id=user_id)

    assert exc_info.value.status_code == 404
    assert f"User '{user_id}' not found!" in exc_info.value.detail
    session.get.assert_called_once_with(User, user_id)


@pytest.mark.asyncio
async def test_validate_document_id_success():
    """Test validate_document_id when document exists."""
    # Arrange
    session = AsyncMock()
    document_id = "test-document-id"
    document = DocumentFactory.build(id=document_id)
    session.get.return_value = document

    # Act
    result = await validate_document_id(session=session, document_id=document_id)

    # Assert
    assert result == document
    session.get.assert_called_once_with(Document, document_id)


@pytest.mark.asyncio
async def test_validate_document_id_not_found():
    """Test validate_document_id when document does not exist."""
    # Arrange
    session = AsyncMock()
    document_id = "non-existent-document-id"
    session.get.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await validate_document_id(session=session, document_id=document_id)

    assert exc_info.value.status_code == 404
    assert f"Document '{document_id}' not found!" in exc_info.value.detail
    session.get.assert_called_once_with(Document, document_id)


@pytest.mark.asyncio
async def test_validate_order_input_success():
    """Test validate_order_input when both payer and payee exist."""
    # Arrange
    session = AsyncMock()
    payer_id = "payer-id"
    payee_id = "payee-id"
    payer = UserFactory.build(id=payer_id)
    payee = UserFactory.build(id=payee_id)
    order_input = OrderInput(amount=100.0, payer_id=payer_id, payee_id=payee_id)

    # Mock validate_user_id to return the users
    with patch("app_sqlalchemy_orm.api.dependencies.validate_user_id") as mock_validate:
        mock_validate.side_effect = [payer, payee]

        # Act
        result = await validate_order_input(session=session, order_input=order_input)

        # Assert
        assert isinstance(result, ValidatedOrder)
        assert result.order_input == order_input
        assert result.payer == payer
        assert result.payee == payee
        assert mock_validate.call_count == 2
        mock_validate.assert_any_call(session=session, user_id=payer_id)
        mock_validate.assert_any_call(session=session, user_id=payee_id)


@pytest.mark.asyncio
async def test_validate_order_input_payer_not_found():
    """Test validate_order_input when payer does not exist."""
    # Arrange
    session = AsyncMock()
    payer_id = "non-existent-payer-id"
    payee_id = "payee-id"
    order_input = OrderInput(amount=100.0, payer_id=payer_id, payee_id=payee_id)

    # Mock validate_user_id to raise an exception for payer
    with patch("app_sqlalchemy_orm.api.dependencies.validate_user_id") as mock_validate:
        mock_validate.side_effect = HTTPException(
            status_code=404, detail=f"User '{payer_id}' not found!"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_order_input(session=session, order_input=order_input)

        assert exc_info.value.status_code == 404
        assert f"User '{payer_id}' not found!" in exc_info.value.detail
        mock_validate.assert_called_once_with(session=session, user_id=payer_id)


@pytest.mark.asyncio
async def test_validate_order_input_payee_not_found():
    """Test validate_order_input when payee does not exist."""
    # Arrange
    session = AsyncMock()
    payer_id = "payer-id"
    payee_id = "non-existent-payee-id"
    payer = UserFactory.build(id=payer_id)
    order_input = OrderInput(amount=100.0, payer_id=payer_id, payee_id=payee_id)

    # Mock validate_user_id to return payer but raise an exception for payee
    with patch("app_sqlalchemy_orm.api.dependencies.validate_user_id") as mock_validate:
        mock_validate.side_effect = [
            payer,
            HTTPException(status_code=404, detail=f"User '{payee_id}' not found!"),
        ]

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_order_input(session=session, order_input=order_input)

        assert exc_info.value.status_code == 404
        assert f"User '{payee_id}' not found!" in exc_info.value.detail
        assert mock_validate.call_count == 2
        mock_validate.assert_any_call(session=session, user_id=payer_id)
        mock_validate.assert_any_call(session=session, user_id=payee_id)
