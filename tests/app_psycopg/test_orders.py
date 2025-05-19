import uuid
from decimal import Decimal
from unittest.mock import patch
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.models import (
    OrderInput,
    User,
    Order,
    OrderInputValidated,
    UserShort,
    ProfessionShort,
)


class UserFactory(ModelFactory[User]):
    __model__ = User


class ProfessionShortFactory(ModelFactory[ProfessionShort]):
    __model__ = ProfessionShort


class UserShortFactory(ModelFactory[UserShort]):
    __model__ = UserShort


class OrderResponseFactory(ModelFactory[Order]):
    __model__ = Order

    @classmethod
    def amount(cls) -> Decimal:
        return Decimal("100.00")


@pytest.fixture
def order_id():
    """Generate a random order ID."""
    return uuid.uuid4().hex


@pytest.fixture
def payer():
    """Create a test payer user."""
    return UserFactory.build(id=uuid.uuid4().hex, name="Payer User")


@pytest.fixture
def payee():
    """Create a test payee user."""
    return UserFactory.build(id=uuid.uuid4().hex, name="Payee User")


@pytest.fixture
def order_input(payer, payee):
    """Create a test order input."""
    return OrderInput(
        amount=Decimal("100.00"),
        payer_id=payer.id,
        payee_id=payee.id,
    )


@pytest.fixture
def payer_response(payer):
    """Create a test payer user response model."""
    return UserShortFactory.build(id=payer.id, name=payer.name)


@pytest.fixture
def payee_response(payee):
    """Create a test payee user response model."""
    return UserShortFactory.build(id=payee.id, name=payee.name)


@pytest.fixture
def order(order_id, payer_response, payee_response):
    """Create a test order."""
    return Order(
        id=order_id,
        amount=Decimal("100.00"),
        payer=payer_response,
        payee=payee_response,
        created_at=datetime.now(),
    )


@pytest.fixture
def validated_order(order_input, payer, payee):
    """Create a validated order."""
    # Create proper User objects with ProfessionShort
    payer_with_profession = UserFactory.build(
        id=payer.id,
        name=payer.name,
        created_at=datetime.now(),
        profession=ProfessionShortFactory.build(),
    )
    payee_with_profession = UserFactory.build(
        id=payee.id,
        name=payee.name,
        created_at=datetime.now(),
        profession=ProfessionShortFactory.build(),
    )

    return OrderInputValidated(
        order_input=order_input,
        payer=payer_with_profession,
        payee=payee_with_profession,
    )


def test_create_order(client: TestClient, mock_db, order, validated_order):
    """Test creating an order."""
    # Setup mock
    mock_db.insert_order.return_value = order.id
    mock_db.get_order.return_value = order

    # We need to patch both validate_order_input and validate_user_id
    # to avoid the validation error
    with (
        patch(
            "app_psycopg.api.dependencies.validate_user_id",
            side_effect=[validated_order.payer, validated_order.payee],
        ),
        patch(
            "app_psycopg.api.routes.orders.validate_order_input",
            return_value=validated_order,
        ),
    ):
        # Make request
        response = client.post(
            "/orders",
            json={
                "amount": str(validated_order.order_input.amount),
                "payer_id": str(validated_order.order_input.payer_id),
                "payee_id": str(validated_order.order_input.payee_id),
            },
        )

    # Print response content for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["id"] == str(order.id)
    assert response_json["amount"] == str(order.amount)
    assert response_json["payer"]["id"] == str(order.payer.id)
    assert response_json["payer"]["name"] == order.payer.name
    assert response_json["payee"]["id"] == str(order.payee.id)
    assert response_json["payee"]["name"] == order.payee.name

    # Assert mock calls
    mock_db.insert_order.assert_called_once_with(validated_order.order_input)
    mock_db.get_order.assert_called_once_with(order.id)


def test_get_order(client: TestClient, mock_db, order):
    """Test getting an order by ID."""
    # Setup mock
    mock_db.get_order.return_value = order

    # Store the actual ID value
    order_id = order.id

    # Create a real Order object to return from the validate_order_id dependency
    real_order = Order(
        id=order_id,
        amount=order.amount,
        payer=order.payer,
        payee=order.payee,
        created_at=order.created_at,
    )

    # Patch the validate_order_id dependency
    with patch(
        "app_psycopg.api.routes.orders.validate_order_id", return_value=real_order
    ):
        # Make request
        response = client.get(f"/orders/{order_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == str(order_id)
    assert response_json["amount"] == str(order.amount)
    assert response_json["payer"]["id"] == str(order.payer.id)
    assert response_json["payer"]["name"] == order.payer.name
    assert response_json["payee"]["id"] == str(order.payee.id)
    assert response_json["payee"]["name"] == order.payee.name
    assert "created_at" in response_json


def test_get_orders(client: TestClient, mock_db, order):
    """Test getting a list of orders."""
    # Setup mock
    mock_db.get_orders.return_value = [order]
    mock_db.get_orders_count.return_value = 1

    # Make request
    response = client.get("/orders")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["id"] == str(order.id)
    assert response_json["items"][0]["amount"] == str(order.amount)
    assert "limit" in response_json
    assert "offset" in response_json
    assert "items_count" in response_json
    assert "total_count" in response_json

    # Assert mock calls
    mock_db.get_orders.assert_called_once_with(limit=10, offset=0, order_by=None)
    mock_db.get_orders_count.assert_called_once()


def test_delete_order(client: TestClient, mock_db, order):
    """Test deleting an order."""
    # Store the actual ID value
    order_id = order.id

    # Patch the validate_order_id dependency
    with patch("app_psycopg.api.routes.orders.validate_order_id", return_value=order):
        # Make request
        response = client.delete(f"/orders/{order_id}")

    # Assert response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Assert mock calls
    mock_db.delete_order.assert_called_once()
