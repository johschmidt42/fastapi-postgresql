import uuid

import pytest
from fastapi.testclient import TestClient
from starlette import status

from app_sqlalchemy.api.dependencies import ValidatedOrder
from app_sqlalchemy.api.models import OrderInput
from conftest import UserResponseFactory, OrderResponseFactory, UserFactory


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


def test_create_order(client: TestClient, mock_session, order, validated_order):
    """Test creating an order."""

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
    response_json = response.json()
    assert isinstance(response_json["id"], str)  # Check that ID is a string
    assert response_json["amount"] == order.amount
    assert response_json["payer"]["id"] == order.payer.id
    assert response_json["payer"]["name"] == order.payer.name
    assert response_json["payee"]["id"] == order.payee.id
    assert response_json["payee"]["name"] == order.payee.name
