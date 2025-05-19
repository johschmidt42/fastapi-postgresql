import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import Company


class CompanyFactory(ModelFactory[Company]):
    __model__ = Company


@pytest.fixture
def company_id():
    """Generate a random company ID."""
    return uuid.uuid4().hex


@pytest.fixture
def company(company_id):
    """Create a test company."""
    return CompanyFactory.build(id=company_id, name="Test Company")


def test_create_company(client: TestClient, mock_db, company):
    """Test creating a company."""
    # Setup mock
    mock_db.insert_company.return_value = company.id

    # Make request
    response = client.post(
        "/companies",
        json={"name": company.name},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == str(company.id)

    # Assert mock calls
    mock_db.insert_company.assert_called_once()


def test_get_company(client: TestClient, mock_db, company):
    """Test getting a company by ID."""
    # Setup mock
    mock_db.get_company.return_value = company

    # Patch the validate_company_id dependency
    with patch(
        "app_psycopg.api.routes.company.validate_company_id",
        return_value=company,
    ):
        # Make request
        response = client.get(f"/companies/{company.id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == str(company.id)
    assert response_json["name"] == company.name
    assert "created_at" in response_json
    assert "last_updated_at" in response_json


def test_get_companies(client: TestClient, mock_db, company):
    """Test getting a list of companies."""
    # Setup mock
    mock_db.get_companies.return_value = [company]
    mock_db.get_companies_count.return_value = 1

    # Make request
    response = client.get("/companies")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == str(company.id)
    assert response_json["items"][0]["name"] == company.name
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json

    # Assert mock calls
    mock_db.get_companies.assert_called_once_with(limit=10, offset=0, order_by=None)
    mock_db.get_companies_count.assert_called_once()


def test_update_company(client: TestClient, mock_db, company):
    """Test updating a company."""
    # Setup mock
    updated_company = Company(
        id=company.id,
        name="Updated Company",
        created_at=company.created_at,
        last_updated_at=company.last_updated_at,
    )
    mock_db.update_company.return_value = company.id
    mock_db.get_company.return_value = updated_company

    # Patch only the validate_company_id dependency
    with patch(
        "app_psycopg.api.routes.company.validate_company_id",
        return_value=company,
    ):
        # Make request
        response = client.put(
            f"/companies/{company.id}",
            json={"name": "Updated Company"},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(company.id)

    # Assert mock calls
    mock_db.update_company.assert_called_once()


def test_patch_company(client: TestClient, mock_db, company):
    """Test patching a company."""
    # Setup mock
    patched_company = Company(
        id=company.id,
        name="Patched Company",
        created_at=company.created_at,
        last_updated_at=company.last_updated_at,
    )
    mock_db.patch_company.return_value = company.id
    mock_db.get_company.return_value = patched_company

    # Patch only the validate_company_id dependency
    with patch(
        "app_psycopg.api.routes.company.validate_company_id",
        return_value=company,
    ):
        # Make request
        response = client.patch(
            f"/companies/{company.id}",
            json={"name": "Patched Company"},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(company.id)

    # Assert mock calls
    mock_db.patch_company.assert_called_once()


def test_delete_company(client: TestClient, mock_db, company):
    """Test deleting a company."""
    # Store the actual ID value
    company_id = company.id

    # Patch only the validate_company_id dependency
    with patch(
        "app_psycopg.api.routes.company.validate_company_id",
        return_value=company,
    ):
        # Make request
        response = client.delete(f"/companies/{company_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Assert mock calls
    mock_db.delete_company.assert_called_once()


def test_get_company_not_found(client: TestClient, mock_db):
    """Test getting a company that doesn't exist."""
    # Setup mock
    mock_db.get_company.return_value = None
    non_existent_id = uuid.uuid4().hex

    # Make request
    response = client.get(f"/companies/{non_existent_id}")

    # Assert response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_create_company_invalid_data(client: TestClient, mock_db):
    """Test creating a company with invalid data."""
    # Make request with empty name
    response = client.post(
        "/companies",
        json={"name": ""},
    )

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Make request with name that's too long
    response = client.post(
        "/companies",
        json={"name": "x" * 51},  # 51 characters, max is 50
    )

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_companies_with_pagination_and_sorting(
    client: TestClient, mock_db, company
):
    """Test getting a list of companies with pagination and sorting."""
    # Setup mock
    mock_db.get_companies.return_value = [company]
    mock_db.get_companies_count.return_value = 1

    # Make request with pagination and sorting
    response = client.get("/companies?limit=5&offset=0&order_by=%2Bname")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["limit"] == 5
    assert response_json["offset"] == 0

    # Assert mock calls with correct parameters
    mock_db.get_companies.assert_called_once()
    # Extract the call arguments
    call_args = mock_db.get_companies.call_args[1]
    assert call_args["limit"] == 5
    assert call_args["offset"] == 0
    assert "order_by" in call_args
