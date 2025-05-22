import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, Request
from psycopg import Connection, AsyncConnection

from app_psycopg.api.dependencies import (
    validate_document_id,
    validate_user_id,
    get_db_conn,
    get_db,
    validate_order_input,
    validate_profession_id,
    validate_profession_input,
    validate_profession_update,
    validate_user_input,
    validate_user_update,
    validate_user_patch,
)
from app_psycopg.api.models import OrderInputValidated
from app_psycopg.db.db import Database
from app_psycopg.api.models import (
    OrderInput,
    Document,
    User,
    Profession,
    ProfessionShort,
    ProfessionInput,
    ProfessionUpdate,
    UserInput,
    UserUpdate,
    UserPatch,
)
from polyfactory.factories.pydantic_factory import ModelFactory


class DocumentFactory(ModelFactory[Document]):
    __model__ = Document

    @classmethod
    def document(cls) -> dict:
        return {"key": "value"}


class ProfessionFactory(ModelFactory[Profession]):
    __model__ = Profession


class ProfessionShortFactory(ModelFactory[ProfessionShort]):
    __model__ = ProfessionShort


class UserFactory(ModelFactory[User]):
    __model__ = User

    @classmethod
    def profession(cls) -> ProfessionShort:
        return ProfessionShortFactory.build()


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
    conn_generator = get_db_conn(mock_request)
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
async def test_validate_profession_id_success():
    """Test validate_profession_id when profession exists."""
    # Arrange
    profession_id = uuid.uuid4()
    profession = ProfessionFactory.build(id=profession_id)

    mock_db = AsyncMock()
    mock_db.get_profession.return_value = profession

    # Act
    result = await validate_profession_id(db=mock_db, profession_id=profession_id)

    # Assert
    assert result == profession
    mock_db.get_profession.assert_called_once_with(profession_id)


@pytest.mark.asyncio
async def test_validate_profession_id_not_found():
    """Test validate_profession_id when profession does not exist."""
    # Arrange
    profession_id = uuid.uuid4()

    mock_db = AsyncMock()
    mock_db.get_profession.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await validate_profession_id(db=mock_db, profession_id=profession_id)

    assert exc_info.value.status_code == 404
    assert f"Profession '{profession_id}' not found!" in exc_info.value.detail
    mock_db.get_profession.assert_called_once_with(profession_id)


@pytest.mark.asyncio
async def test_validate_profession_input():
    """Test validate_profession_input."""
    # Arrange
    profession_input = ProfessionInput(name="Test Profession")

    # Act
    result = await validate_profession_input(profession_input=profession_input)

    # Assert
    assert result == profession_input


@pytest.mark.asyncio
async def test_validate_profession_update():
    """Test validate_profession_update."""
    # Arrange
    profession_update = ProfessionUpdate(name="Updated Profession")

    # Act
    result = await validate_profession_update(profession_update=profession_update)

    # Assert
    assert result == profession_update


@pytest.mark.asyncio
async def test_validate_user_input():
    """Test validate_user_input."""
    # Arrange
    profession_id = uuid.uuid4()
    user_input = UserInput(name="Test User", profession_id=profession_id)
    profession = ProfessionFactory.build(id=profession_id)

    mock_db = AsyncMock()

    # Mock validate_profession_id to return the profession
    with patch("app_psycopg.api.dependencies.validate_profession_id") as mock_validate:
        mock_validate.return_value = profession

        # Act
        result = await validate_user_input(db=mock_db, user_input=user_input)

        # Assert
        assert result == user_input
        mock_validate.assert_called_once_with(db=mock_db, profession_id=profession_id)


@pytest.mark.asyncio
async def test_validate_user_update():
    """Test validate_user_update."""
    # Arrange
    profession_id = uuid.uuid4()
    user_update = UserUpdate(name="Updated User", profession_id=profession_id)
    profession = ProfessionFactory.build(id=profession_id)

    mock_db = AsyncMock()

    # Mock validate_profession_id to return the profession
    with patch("app_psycopg.api.dependencies.validate_profession_id") as mock_validate:
        mock_validate.return_value = profession

        # Act
        result = await validate_user_update(db=mock_db, user_update=user_update)

        # Assert
        assert result == user_update
        mock_validate.assert_called_once_with(db=mock_db, profession_id=profession_id)


@pytest.mark.asyncio
async def test_validate_user_patch_with_profession():
    """Test validate_user_patch with profession_id."""
    # Arrange
    profession_id = uuid.uuid4()
    user_patch = UserPatch(name="Patched User", profession_id=profession_id)
    profession = ProfessionFactory.build(id=profession_id)

    mock_db = AsyncMock()

    # Mock validate_profession_id to return the profession
    with patch("app_psycopg.api.dependencies.validate_profession_id") as mock_validate:
        mock_validate.return_value = profession

        # Act
        result = await validate_user_patch(db=mock_db, user_patch=user_patch)

        # Assert
        assert result == user_patch
        mock_validate.assert_called_once_with(db=mock_db, profession_id=profession_id)


@pytest.mark.asyncio
async def test_validate_user_patch_without_profession():
    """Test validate_user_patch without profession_id."""
    # Arrange
    user_patch = UserPatch(name="Patched User")

    mock_db = AsyncMock()

    # Act
    result = await validate_user_patch(db=mock_db, user_patch=user_patch)

    # Assert
    assert result == user_patch


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
        assert isinstance(result, OrderInputValidated)
        assert result.order_input == order_input
        assert result.payer == payer
        assert result.payee == payee
        assert mock_validate.call_count == 2
        mock_validate.assert_any_call(db=mock_db, user_id=payer_id)
        mock_validate.assert_any_call(db=mock_db, user_id=payee_id)
