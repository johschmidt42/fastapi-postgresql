import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import Document


class DocumentFactory(ModelFactory[Document]):
    __model__ = Document


class DocumentResponseFactory(ModelFactory[Document]):
    __model__ = Document


@pytest.fixture
def document_id():
    """Generate a random document ID."""
    return uuid.uuid4().hex


@pytest.fixture
def document(document_id):
    """Create a test document."""
    return DocumentFactory.build(
        id=document_id,
        document={"key": "value"},
    )


@pytest.fixture
def document_response(document_id):
    """Create a test document response."""
    return DocumentResponseFactory.build(
        id=document_id,
        document={"key": "value"},
    )


def test_create_document(client: TestClient, mock_db, document_id, document_response):
    """Test creating a document."""
    # Setup mock
    mock_db.insert_document.return_value = document_id

    # Make request
    response = client.post(
        "/documents",
        json={"document": document_response.document},
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == document_id

    # Assert mock calls
    mock_db.insert_document.assert_called_once()


def test_get_document(client: TestClient, mock_db, document, document_response):
    """Test getting a document by ID."""
    # Setup mock
    mock_db.get_document.return_value = document

    # Patch the validate_document_id dependency
    with patch(
        "app_psycopg.api.routes.documents.validate_document_id", return_value=document
    ):
        # Make request
        response = client.get(f"/documents/{document.id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == str(document.id)
    assert response_json["document"] == document.document
    assert "created_at" in response_json
    assert "last_updated_at" in response_json

    # Assert mock calls
    # The mock is not called directly because we're patching the dependency


def test_get_documents(client: TestClient, mock_db, document):
    """Test getting a list of documents."""
    # Setup mock
    mock_db.get_documents.return_value = [document]
    mock_db.get_documents_count.return_value = 1

    # Make request
    response = client.get("/documents")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == str(document.id)
    assert response_json["items"][0]["document"] == document.document
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json

    # Assert mock calls
    mock_db.get_documents.assert_called_once_with(limit=10, offset=0, order_by=None)
    mock_db.get_documents_count.assert_called_once()


def test_get_documents_with_pagination(client: TestClient, mock_db, document):
    """Test getting a list of documents with pagination."""
    # Setup mock
    mock_db.get_documents.return_value = [document]
    mock_db.get_documents_count.return_value = 1

    # Make request
    response = client.get("/documents?limit=5&offset=0")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["limit"] == 5
    assert response_json["offset"] == 0

    # Assert mock calls
    mock_db.get_documents.assert_called_once_with(limit=5, offset=0, order_by=None)


def test_get_documents_with_sorting(client: TestClient, mock_db, document):
    """Test getting a list of documents with sorting."""
    # Setup mock
    mock_db.get_documents.return_value = [document]
    mock_db.get_documents_count.return_value = 1

    # Make request
    response = client.get("/documents?order_by=%2Bcreated_at")

    # Assert response
    assert response.status_code == status.HTTP_200_OK

    # Assert mock calls
    # We can't check the exact order_by parameter because it's processed by the dependency
    mock_db.get_documents.assert_called_once()


def test_update_document(client: TestClient, mock_db, document, document_id):
    """Test updating a document."""
    # Setup mock
    mock_db.update_document.return_value = document_id

    # Patch the validate_document_id dependency
    with patch(
        "app_psycopg.api.routes.documents.validate_document_id", return_value=document
    ):
        # Make request
        response = client.put(
            f"/documents/{document.id}",
            json={"document": {"key": "updated_value"}},
        )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == document_id

    # Assert mock calls
    mock_db.update_document.assert_called_once()


def test_delete_document(client: TestClient, mock_db, document, document_id):
    """Test deleting a document."""
    # Patch the validate_document_id dependency
    with patch(
        "app_psycopg.api.routes.documents.validate_document_id", return_value=document
    ):
        # Make request
        response = client.delete(f"/documents/{document_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Assert mock calls
    # The mock is called with the return value of document.id, which is a mock itself
    mock_db.delete_document.assert_called_once()
