import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette import status

from app_psycopg.db.db_models import User
from tests.app_psycopg.conftest import UserFactory


@pytest.fixture
def user_id():
    """Generate a random user ID."""
    return uuid.uuid4().hex


@pytest.fixture
def user(user_id):
    """Create a test user."""
    return UserFactory.build(id=user_id, name="Test User")


def test_create_user(client: TestClient, mock_db, user):
    """Test creating a user."""
    # Setup mock
    mock_db.insert_user.return_value = user.id
    mock_db.get_user.return_value = user

    # Make request
    response = client.post(
        "/users",
        json={"name": user.name},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user.id

    # Assert mock calls
    mock_db.insert_user.assert_called_once()
    mock_db.get_user.assert_called_once_with(user.id)


def test_get_user(client: TestClient, mock_db, user):
    """Test getting a user by ID."""
    # Setup mock
    mock_db.get_user.return_value = user

    # Patch the validate_user_id dependency
    with patch("app_psycopg.api.routes.users.validate_user_id", return_value=user):
        # Make request
        response = client.get(f"/users/{user.id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user.id,
        "name": user.name,
    }


def test_get_users(client: TestClient, mock_db, user):
    """Test getting a list of users."""
    # Setup mock
    mock_db.get_users.return_value = [user]

    # Make request
    response = client.get("/users")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": user.id,
            "name": user.name,
        }
    ]

    # Assert mock calls
    mock_db.get_users.assert_called_once_with(limit=10, offset=0)


def test_update_user(client: TestClient, mock_db, user):
    """Test updating a user."""
    # Setup mock
    updated_user = User(id=user.id, name="Updated User")
    mock_db.update_user.return_value = user.id
    mock_db.get_user.return_value = updated_user

    # Patch only the validate_user_id dependency
    with patch("app_psycopg.api.routes.users.validate_user_id", return_value=user):
        # Make request
        response = client.put(
            f"/users/{user.id}",
            json={"name": "Updated User"},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user.id

    # Assert mock calls
    mock_db.update_user.assert_called_once()


def test_delete_user(client: TestClient, mock_db, user):
    """Test deleting a user."""
    # Patch only the validate_user_id dependency
    with patch("app_psycopg.api.routes.users.validate_user_id", return_value=user):
        # Make request
        response = client.delete(f"/users/{user.id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Assert mock calls
    # The mock is called with the return value of user.id, which is a mock itself
    mock_db.delete_user.assert_called_once()
