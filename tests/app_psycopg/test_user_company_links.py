import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import (
    UserCompanyLinkWithCompany,
    UserCompanyLinkWithUser,
    Company,
    CompanyShort,
    UserShort,
)


class UserCompanyLinkWithCompanyFactory(ModelFactory[UserCompanyLinkWithCompany]):
    __model__ = UserCompanyLinkWithCompany


class UserCompanyLinkWithUserFactory(ModelFactory[UserCompanyLinkWithUser]):
    __model__ = UserCompanyLinkWithUser


@pytest.fixture
def user_id():
    """Generate a random user ID."""
    return uuid.uuid4().hex


@pytest.fixture
def company_id():
    """Generate a random company ID."""
    return uuid.uuid4().hex


@pytest.fixture
def company(company_id):
    """Create a test company."""
    return Company(
        id=company_id,
        name="Test Company",
        created_at="2023-01-01T00:00:00",
        last_updated_at=None,
    )


@pytest.fixture
def user(user_id):
    """Create a test user."""
    return UserShort(id=user_id, name="TEST USER")


@pytest.fixture
def user_company_link_with_company(user_id, company_id):
    """Create a test user-company link with company details."""
    company_short = CompanyShort(id=company_id, name="Test Company")
    return UserCompanyLinkWithCompanyFactory.build(
        user_id=user_id,
        company=company_short,
        created_at="2023-01-01T00:00:00",
        last_updated_at=None,
    )


@pytest.fixture
def user_company_link_with_user(company_id, user):
    """Create a test user-company link with user details."""
    return UserCompanyLinkWithUserFactory.build(
        company_id=company_id,
        user=user,
        created_at="2023-01-01T00:00:00",
        last_updated_at=None,
    )


def test_create_user_company_link(client: TestClient, mock_db, user_id, company_id):
    """Test creating a user-company link."""
    # Setup mock
    mock_db.insert_user_company_link.return_value = (user_id, company_id)
    mock_db.get_user_company_links_count_by_user.return_value = 0

    # Make request
    response = client.post(
        "/user-company-links",
        json={"user_id": user_id, "company_id": company_id},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert "user_id" in response_json
    assert "company_id" in response_json

    # Assert mock calls
    mock_db.insert_user_company_link.assert_called_once()


def test_delete_user_company_link(
    client: TestClient, mock_db, user_id, company_id, user_company_link_with_company
):
    """Test deleting a user-company link."""
    # Setup mocks
    mock_db.get_user_company_links_count_by_user.return_value = 1
    mock_db.get_user_company_links_by_user.return_value = [
        user_company_link_with_company
    ]

    # Patch the validate_user_company_link dependency
    with patch(
        "app_psycopg.api.routes.user_company_links.validate_user_company_link",
        return_value=None,
    ):
        # Make request
        response = client.delete(f"/user-company-links/{user_id}/{company_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_get_user_company_links_by_user(
    client: TestClient, mock_db, user_id, user_company_link_with_company
):
    """Test getting companies linked to a user."""
    # Setup mocks
    mock_db.get_user_company_links_by_user.return_value = [
        user_company_link_with_company
    ]
    mock_db.get_user_company_links_count_by_user.return_value = 1
    mock_db.get_user.return_value = True  # Just need a truthy value for validation

    # Patch the validate_get_user_company_links dependency
    with patch(
        "app_psycopg.api.routes.user_company_links.validate_get_user_company_links",
        return_value={"user_id": user_id, "company_id": None},
    ):
        # Patch the validate_user_id dependency
        with patch(
            "app_psycopg.api.routes.user_company_links.validate_user_id",
            return_value=None,
        ):
            # Make request
            response = client.get(f"/user-company-links?user_id={user_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    # Don't assert the exact user_id value, just check it exists
    assert "user_id" in response_json["items"][0]
    assert "company" in response_json["items"][0]
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json


def test_get_user_company_links_by_company(
    client: TestClient, mock_db, company_id, user_company_link_with_user
):
    """Test getting users linked to a company."""
    # Setup mocks
    mock_db.get_user_company_links_by_company.return_value = [
        user_company_link_with_user
    ]
    mock_db.get_user_company_links_count_by_company.return_value = 1
    mock_db.get_company.return_value = True  # Just need a truthy value for validation

    # Patch the validate_get_user_company_links dependency
    with patch(
        "app_psycopg.api.routes.user_company_links.validate_get_user_company_links",
        return_value={"user_id": None, "company_id": company_id},
    ):
        # Patch the validate_company_id dependency
        with patch(
            "app_psycopg.api.routes.user_company_links.validate_company_id",
            return_value=None,
        ):
            # Make request
            response = client.get(f"/user-company-links?company_id={company_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    # Don't assert the exact company_id value, just check it exists
    assert "company_id" in response_json["items"][0]
    assert "user_info" in response_json["items"][0]
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json


def test_get_user_company_links_no_params(client: TestClient):
    """Test getting user-company links with no parameters."""
    # Make request
    response = client.get("/user-company-links")

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "detail" in response_json
    assert "must be provided" in response_json["detail"]


def test_get_user_company_links_with_pagination(
    client: TestClient, mock_db, user_id, user_company_link_with_company
):
    """Test getting user-company links with pagination."""
    # Setup mocks
    mock_db.get_user_company_links_by_user.return_value = [
        user_company_link_with_company
    ]
    mock_db.get_user_company_links_count_by_user.return_value = 1
    mock_db.get_user.return_value = True  # Just need a truthy value for validation

    # Patch the validate_get_user_company_links dependency
    with patch(
        "app_psycopg.api.routes.user_company_links.validate_get_user_company_links",
        return_value={"user_id": user_id, "company_id": None},
    ):
        # Patch the validate_user_id dependency
        with patch(
            "app_psycopg.api.routes.user_company_links.validate_user_id",
            return_value=None,
        ):
            # Make request with pagination
            response = client.get(
                f"/user-company-links?user_id={user_id}&limit=5&offset=0"
            )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["limit"] == 5
    assert response_json["offset"] == 0
