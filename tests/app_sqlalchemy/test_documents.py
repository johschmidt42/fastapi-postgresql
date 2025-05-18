import uuid

import pytest
from fastapi.testclient import TestClient
from starlette import status


@pytest.fixture
def document_id():
    """Generate a random document ID."""
    return uuid.uuid4().hex


def test_create_document(client: TestClient, document_response):
    """Test creating a document."""
    # Make request
    response = client.post(
        "/documents",
        json={"document": document_response.document},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(response.json(), str)  # Should return a document ID


def test_get_document(client: TestClient, document_id, document_response):
    """Test getting a document by ID."""
    # Make request
    response = client.get(f"/documents/{document_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == document_id
    assert response_json["document"] == document_response.document
    assert "created_at" in response_json
    assert "last_updated_at" in response_json


def test_get_documents(client: TestClient):
    """Test getting a list of documents."""
    # Make request
    response = client.get("/documents")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "document" in response.json()[0]


def test_get_documents_with_pagination(client: TestClient):
    """Test getting a list of documents with pagination."""
    # Make request with limit and offset
    response = client.get("/documents?limit=5&offset=2")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

    # We can't assert the exact number of items because it depends on the database state
    # But we can check that the response is a list and has the expected structure
    if len(response.json()) > 0:
        assert "id" in response.json()[0]
        assert "document" in response.json()[0]


def test_get_documents_with_sorting(client: TestClient):
    """Test getting a list of documents with sorting."""
    # Test ascending sort
    response = client.get("/documents?order_by=%2Bcreated_at")
    assert response.status_code == status.HTTP_200_OK

    # Test descending sort
    response = client.get("/documents?order_by=%2Dlast_updated_at")
    assert response.status_code == status.HTTP_200_OK

    # Test multiple sort fields
    response = client.get(
        "/documents?order_by=%2Bcreated_at&order_by=%2Dlast_updated_at"
    )
    assert response.status_code == status.HTTP_200_OK


def test_update_document(client: TestClient, document_id):
    """Test updating a document."""
    # Make request
    response = client.put(
        f"/documents/{document_id}",
        json={"document": {"key": "updated_value"}},
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), str)  # Should return a document ID


def test_delete_document(client: TestClient, document_id):
    """Test deleting a document."""
    # Make request
    response = client.delete(f"/documents/{document_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
