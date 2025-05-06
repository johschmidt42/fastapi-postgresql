import uuid

import pytest
from fastapi.testclient import TestClient
from starlette import status


@pytest.fixture
def user_id():
    """Generate a random user ID."""
    return uuid.uuid4().hex


def test_create_user(client: TestClient, user_response):
    """Test creating a user."""
    # Make request
    response = client.post(
        "/users",
        json={"name": user_response.name},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(response.json(), str)  # Should return a user ID


def test_get_user(client: TestClient, user_id, user_response):
    """Test getting a user by ID."""
    # Make request
    response = client.get(f"/users/{user_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user_id,
        "name": user_response.name,
    }


def test_get_users(client: TestClient):
    """Test getting a list of users."""
    # Make request
    response = client.get("/users")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


def test_update_user(client: TestClient, user_id):
    """Test updating a user."""
    # Make request
    response = client.put(
        f"/users/{user_id}",
        json={"name": "Updated User"},
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), str)  # Should return a user ID


def test_delete_user(client: TestClient, user_id):
    """Test deleting a user."""
    # Make request
    response = client.delete(f"/users/{user_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
