from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory

from app_psycopg.api.app import app as psycopg_app
from app_psycopg.api.dependencies import get_conn, get_db
from app_psycopg.db.db import Database
from app_psycopg.db.db_models import User, Order


class UserFactory(ModelFactory[User]):
    __model__ = User


class OrderFactory(ModelFactory[Order]):
    __model__ = Order

    @classmethod
    def build(cls, **kwargs):
        """Build an Order instance with proper User objects for payer and payee."""
        if "payer" not in kwargs:
            kwargs["payer"] = UserFactory.build()
        if "payee" not in kwargs:
            kwargs["payee"] = UserFactory.build()
        return super().build(**kwargs)


@pytest.fixture
def app() -> FastAPI:
    """Get FastAPI application."""
    return psycopg_app


@pytest.fixture
def mock_conn():
    """Create a mock database connection."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_db():
    """Create a mock Database instance."""
    mock = AsyncMock(spec=Database)
    return mock


@pytest.fixture
def client(app: FastAPI, mock_conn, mock_db) -> TestClient:
    """Get test client for FastAPI application with mocked dependencies."""

    # Override the get_conn dependency
    async def override_get_conn():
        yield mock_conn

    # Override the get_db dependency
    def override_get_db(conn=Depends(override_get_conn)):
        return mock_db

    app.dependency_overrides[get_conn] = override_get_conn
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear the dependency overrides after the test
    app.dependency_overrides.clear()
