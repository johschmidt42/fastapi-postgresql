import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from starlette import status

from app_psycopg.api.dependencies import ValidatedOrder
from app_psycopg.api.models import OrderInput, UserResponseModel, OrderResponseModel
from app_psycopg.db.db_models import User


class UserFactory(ModelFactory[User]):
    __model__ = User


class UserResponseFactory(ModelFactory[UserResponseModel]):
    __model__ = UserResponseModel


class OrderResponseFactory(ModelFactory[OrderResponseModel]):
    __model__ = OrderResponseModel


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
        amount=100.0,
        payer_id=payer.id,
        payee_id=payee.id,
    )


@pytest.fixture
def payer_response(payer):
    """Create a test payer user response model."""
    return UserResponseFactory.build(id=payer.id, name=payer.name)


@pytest.fixture
def payee_response(payee):
    """Create a test payee user response model."""
    return UserResponseFactory.build(id=payee.id, name=payee.name)


@pytest.fixture
def order(order_id, payer_response, payee_response):
    """Create a test order."""
    return OrderResponseFactory.build(
        id=order_id,
        amount=100.0,
        payer=payer_response,
        payee=payee_response,
    )


@pytest.fixture
def validated_order(order_input, payer, payee):
    """Create a validated order."""
    return ValidatedOrder(
        order_input=order_input,
        payer=payer,
        payee=payee,
    )


def test_create_order(client: TestClient, mock_db, order, validated_order):
    """Test creating an order."""
    # Setup mock
    mock_db.insert_order.return_value = order.id
    mock_db.get_order.return_value = order

    # Patch only the validate_order_input dependency
    with patch(
        "app_psycopg.api.routes.orders.validate_order_input",
        return_value=validated_order,
    ):
        # Make request
        response = client.post(
            "/orders",
            json={
                "amount": validated_order.order_input.amount,
                "payer_id": validated_order.order_input.payer_id,
                "payee_id": validated_order.order_input.payee_id,
            },
        )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": order.id,
        "amount": order.amount,
        "payer": {
            "id": order.payer.id,
            "name": order.payer.name,
        },
        "payee": {
            "id": order.payee.id,
            "name": order.payee.name,
        },
    }

    # Assert mock calls
    mock_db.insert_order.assert_called_once_with(validated_order.order_input)
    mock_db.get_order.assert_called_once_with(order.id)
