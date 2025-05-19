import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import Profession


class ProfessionFactory(ModelFactory[Profession]):
    __model__ = Profession


@pytest.fixture
def profession_id():
    """Generate a random profession ID."""
    return uuid.uuid4().hex


@pytest.fixture
def profession(profession_id):
    """Create a test profession."""
    return ProfessionFactory.build(id=profession_id, name="Test Profession")


def test_create_profession(client: TestClient, mock_db, profession):
    """Test creating a profession."""
    # Setup mock
    mock_db.insert_profession.return_value = profession.id

    # Make request
    response = client.post(
        "/professions",
        json={"name": profession.name},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == str(profession.id)

    # Assert mock calls
    mock_db.insert_profession.assert_called_once()


def test_get_profession(client: TestClient, mock_db, profession):
    """Test getting a profession by ID."""
    # Setup mock
    mock_db.get_profession.return_value = profession

    # Patch the validate_profession_id dependency
    with patch(
        "app_psycopg.api.routes.profession.validate_profession_id",
        return_value=profession,
    ):
        # Make request
        response = client.get(f"/professions/{profession.id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == str(profession.id)
    assert response_json["name"] == profession.name
    assert "created_at" in response_json
    assert "last_updated_at" in response_json


def test_get_professions(client: TestClient, mock_db, profession):
    """Test getting a list of professions."""
    # Setup mock
    mock_db.get_professions.return_value = [profession]
    mock_db.get_professions_count.return_value = 1

    # Make request
    response = client.get("/professions")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == str(profession.id)
    assert response_json["items"][0]["name"] == profession.name
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json

    # Assert mock calls
    mock_db.get_professions.assert_called_once_with(limit=10, offset=0, order_by=None)
    mock_db.get_professions_count.assert_called_once()


def test_update_profession(client: TestClient, mock_db, profession):
    """Test updating a profession."""
    # Setup mock
    updated_profession = Profession(
        id=profession.id,
        name="Updated Profession",
        created_at=profession.created_at,
        last_updated_at=profession.last_updated_at,
    )
    mock_db.update_profession.return_value = profession.id
    mock_db.get_profession.return_value = updated_profession

    # Patch only the validate_profession_id dependency
    with patch(
        "app_psycopg.api.routes.profession.validate_profession_id",
        return_value=profession,
    ):
        # Make request
        response = client.put(
            f"/professions/{profession.id}",
            json={"name": "Updated Profession"},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(profession.id)

    # Assert mock calls
    mock_db.update_profession.assert_called_once()


def test_delete_profession(client: TestClient, mock_db, profession):
    """Test deleting a profession."""
    # Store the actual ID value
    profession_id = profession.id

    # Patch only the validate_profession_id dependency
    with patch(
        "app_psycopg.api.routes.profession.validate_profession_id",
        return_value=profession,
    ):
        # Make request
        response = client.delete(f"/professions/{profession_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Assert mock calls
    mock_db.delete_profession.assert_called_once()
