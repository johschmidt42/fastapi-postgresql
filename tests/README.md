# Unit Tests for FastAPI PostgreSQL

This directory contains unit tests for the FastAPI PostgreSQL applications.

## Test Structure

The tests are organized by application:

- `app_psycopg/`: Tests for the psycopg3 implementation
- `app_sqlalchemy/`: Tests for the SQLAlchemy implementation

Each application has its own test fixtures in `conftest.py` and test files for different routes.

## Testing Approach

The tests follow the best practices from
the [FastAPI testing documentation](https://fastapi.tiangolo.com/tutorial/testing/#using-testclient), particularly
regarding dependency injection.

### Key Features

1. **Dependency Injection**: We use dependency overrides to replace database connections with mocks.
2. **Polyfactory**: We use [polyfactory](https://github.com/litestar-org/polyfactory) to generate test data for Pydantic
   models.

## Running Tests

To run the tests, use pytest:

```bash
# Run all tests
pytest

# Run tests for a specific application
pytest tests/app_psycopg/
pytest tests/app_sqlalchemy/

# Run tests with coverage
pytest --cov=src
```

## Test Files

### app_psycopg

- `test_users.py`: Tests for user endpoints (create, get, update, delete)
- `test_orders.py`: Tests for order endpoints (create)

### app_sqlalchemy

- `test_users.py`: Tests for user endpoints (create, get, update, delete)
- `test_orders.py`: Tests for order endpoints (create)
