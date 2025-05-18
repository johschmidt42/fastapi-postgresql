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
    response_json = response.json()
    assert response_json["id"] == user_id
    assert response_json["name"] == user_response.name
    assert "created_at" in response_json
    assert "last_updated_at" in response_json


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


def test_get_users_with_pagination(client: TestClient):
    """Test getting a list of users with pagination."""
    # Make request with limit and offset
    response = client.get("/users?limit=5&offset=2")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

    # We can't assert the exact number of items because it depends on the database state
    # But we can check that the response is a list and has the expected structure
    if len(response.json()) > 0:
        assert "id" in response.json()[0]
        assert "name" in response.json()[0]


def test_get_users_with_sorting(client: TestClient):
    """Test getting a list of users with sorting."""
    # Test ascending sort by name
    response = client.get("/users?order_by=%2Bname")
    assert response.status_code == status.HTTP_200_OK

    # Test descending sort by name
    response = client.get("/users?order_by=%2Dname")
    assert response.status_code == status.HTTP_200_OK

    # Test sort by created_at
    response = client.get("/users?order_by=%2Bcreated_at")
    assert response.status_code == status.HTTP_200_OK

    # Test sort by last_updated_at
    response = client.get("/users?order_by=%2Dlast_updated_at")
    assert response.status_code == status.HTTP_200_OK

    # Test multiple sort fields
    response = client.get("/users?order_by=%2Bname&order_by=%2Dcreated_at")
    assert response.status_code == status.HTTP_200_OK


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
