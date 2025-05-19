import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import User


class UserFactory(ModelFactory[User]):
    __model__ = User


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

    # Make request
    response = client.post(
        "/users",
        json={"name": user.name, "profession_id": str(user.profession.id)},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == str(user.id)

    # Assert mock calls
    mock_db.insert_user.assert_called_once()


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
    response_json = response.json()
    assert response_json["id"] == str(user.id)
    assert response_json["name"] == user.name
    assert "created_at" in response_json
    assert "last_updated_at" in response_json


def test_get_users(client: TestClient, mock_db, user):
    """Test getting a list of users."""
    # Setup mock
    mock_db.get_users.return_value = [user]

    # Make request
    response = client.get("/users")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == str(user.id)
    assert response_json["items"][0]["name"] == user.name
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json

    # Assert mock calls
    mock_db.get_users.assert_called_once_with(limit=10, offset=0, order_by=None)


def test_update_user(client: TestClient, mock_db, user):
    """Test updating a user."""
    # Setup mock
    updated_user = User(
        id=user.id,
        name="Updated User",
        created_at=user.created_at,
        last_updated_at=user.last_updated_at,
        profession=user.profession,
    )
    mock_db.update_user.return_value = user.id
    mock_db.get_user.return_value = updated_user

    # Patch only the validate_user_id dependency
    with patch("app_psycopg.api.routes.users.validate_user_id", return_value=user):
        # Make request
        response = client.put(
            f"/users/{user.id}",
            json={"name": "Updated User", "profession_id": str(user.profession.id)},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(user.id)

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


def test_patch_user(client: TestClient, mock_db, user):
    """Test patching a user."""
    # Setup mock
    patched_user = User(
        id=user.id,
        name="Patched User",
        created_at=user.created_at,
        last_updated_at=user.last_updated_at,
        profession=user.profession,
    )
    mock_db.patch_user.return_value = user.id
    mock_db.get_user.return_value = patched_user

    # Patch only the validate_user_id dependency
    with patch("app_psycopg.api.routes.users.validate_user_id", return_value=user):
        # Make request
        response = client.patch(
            f"/users/{user.id}",
            json={"name": "Patched User"},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(user.id)

    # Assert mock calls
    mock_db.patch_user.assert_called_once()
