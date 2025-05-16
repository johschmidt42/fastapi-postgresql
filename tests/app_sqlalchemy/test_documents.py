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
    assert response.json() == {
        "id": document_id,
        "document": document_response.document,
    }


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
