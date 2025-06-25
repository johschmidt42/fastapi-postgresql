from typing import Annotated
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

import pytest
from fastapi import FastAPI, Depends, Body
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_orm.api.app import app as sqlalchemy_app
from app_sqlalchemy_orm.api.dependencies import (
    get_db_session,
    validate_user_id,
    validate_order_input,
    validate_document_id,
    ValidatedOrder,
)
from app_sqlalchemy_orm.api.models import (
    UserResponseModel,
    OrderResponseModel,
    OrderInput,
    DocumentResponseModel,
)
from app_sqlalchemy_orm.db.db_models import User, Document


class UserResponseFactory(ModelFactory[UserResponseModel]):
    __model__ = UserResponseModel


class OrderResponseFactory(ModelFactory[OrderResponseModel]):
    __model__ = OrderResponseModel


class DocumentResponseFactory(ModelFactory[DocumentResponseModel]):
    __model__ = DocumentResponseModel


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User


class DocumentFactory(SQLAlchemyFactory[Document]):
    __model__ = Document


@pytest.fixture
def app() -> FastAPI:
    """Get FastAPI application."""
    return sqlalchemy_app


@pytest.fixture
def user_response():
    """Create a UserResponseModel for testing."""
    return UserResponseFactory.build()


@pytest.fixture
def order_response():
    """Create an OrderResponseModel for testing."""
    return OrderResponseFactory.build()


@pytest.fixture
def document_response():
    """Create a DocumentResponseModel for testing."""
    return DocumentResponseFactory.build(document={"key": "value"})


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession for testing."""
    mock = AsyncMock()

    # Mock the execute method to return a result with users or documents
    async def mock_execute(query):
        class MockScalars:
            def all(self):
                query_str = str(query)
                # Check if the query is for documents or users based on the query string
                if "Document" in query_str or "documents" in query_str:
                    return [
                        DocumentFactory.build(
                            id="test-doc-id",
                            document={"key": "value"},
                            created_at=datetime.now(),
                        )
                    ]
                # Default to returning User objects for all other queries
                return [UserFactory.build(id="test-id")]

        class MockResult:
            def scalars(self):
                return MockScalars()

        return MockResult()

    # Set up the mock methods
    mock.execute = mock_execute
    mock.add = MagicMock()
    mock.delete = AsyncMock()

    return mock


@pytest.fixture
def client(
    app: FastAPI, mock_session, user_response, order_response, document_response
) -> TestClient:
    """Get test client for FastAPI application with mocked dependencies."""

    # Override the get_db_session dependency
    async def override_get_db_session():
        yield mock_session

    # Override the validate_user_id dependency
    async def override_validate_user_id(user_id: str):
        return UserFactory.build(id=user_id, name=user_response.name)

    # Override the validate_document_id dependency
    async def override_validate_document_id(document_id: str):
        return DocumentFactory.build(
            id=document_id,
            document=document_response.document,
            created_at=datetime.now(),
        )

    # Override the validate_order_input dependency
    async def override_validate_order_input(
        session: Annotated[AsyncSession, Depends(get_db_session)],
        order_input: Annotated[OrderInput, Body(...)],
    ):
        payer = UserFactory.build(id=order_input.payer_id, name="Payer User")
        payee = UserFactory.build(id=order_input.payee_id, name="Payee User")

        return ValidatedOrder(order_input=order_input, payer=payer, payee=payee)

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[validate_user_id] = override_validate_user_id
    app.dependency_overrides[validate_document_id] = override_validate_document_id
    app.dependency_overrides[validate_order_input] = override_validate_order_input

    with TestClient(app) as test_client:
        yield test_client

    # Clear the dependency overrides after the test
    app.dependency_overrides.clear()
