import pytest
from sqlalchemy import Select, Column, Integer, String
from sqlalchemy.orm import declarative_base
from app_sqlalchemy_orm.api.sorting import (
    create_order_by_enum,
    _parse_str_order_by,
    parse_order_by,
    create_order_by_query,
    check_for_duplicates,
    validate_order_by_query_params,
    Direction,
    OrderByField,
)

# Create a test model for SQLAlchemy queries
Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


def test_create_order_by_enum():
    """Test create_order_by_enum function."""
    # Test with a list of field names
    fields = ["name", "age"]
    enum_class = create_order_by_enum(fields)

    # Check that the enum has the expected values
    assert "+name" in enum_class.__members__
    assert "-name" in enum_class.__members__
    assert "+age" in enum_class.__members__
    assert "-age" in enum_class.__members__

    # Check that the enum values are correct
    assert enum_class["+name"].value == "+name"
    assert enum_class["-name"].value == "-name"
    assert enum_class["+age"].value == "+age"
    assert enum_class["-age"].value == "-age"


def test_parse_str_order_by():
    """Test _parse_str_order_by function."""
    # Create a test enum
    TestEnum = create_order_by_enum(["name"])

    # Test with ascending direction
    field = _parse_str_order_by(TestEnum["+name"])
    assert field.name == "name"
    assert field.direction == Direction.ASC

    # Test with descending direction
    field = _parse_str_order_by(TestEnum["-name"])
    assert field.name == "name"
    assert field.direction == Direction.DESC


def test_parse_order_by():
    """Test parse_order_by function."""
    # Create a test enum
    TestEnum = create_order_by_enum(["name", "age"])

    # Test with multiple fields
    fields = parse_order_by({TestEnum["+name"], TestEnum["-age"]})
    assert len(fields) == 2

    # Check that the fields are parsed correctly
    name_field = next(f for f in fields if f.name == "name")
    age_field = next(f for f in fields if f.name == "age")
    assert name_field.direction == Direction.ASC
    assert age_field.direction == Direction.DESC


def test_create_order_by_query():
    """Test create_order_by_query function."""
    # Create a test query
    query = Select(TestModel)

    # Test with ascending direction
    fields = [OrderByField(name="name", direction=Direction.ASC)]
    result = create_order_by_query(query, fields, TestModel)

    # We can't easily check the SQL directly, but we can check that the result is a Select object
    assert isinstance(result, Select)

    # Test with descending direction
    fields = [OrderByField(name="name", direction=Direction.DESC)]
    result = create_order_by_query(query, fields, TestModel)
    assert isinstance(result, Select)

    # Test with multiple fields
    fields = [
        OrderByField(name="name", direction=Direction.ASC),
        OrderByField(name="age", direction=Direction.DESC),
    ]
    result = create_order_by_query(query, fields, TestModel)
    assert isinstance(result, Select)

    # Test with empty fields list
    fields = []
    result = create_order_by_query(query, fields, TestModel)
    assert result == query  # Should return the original query unchanged


def test_check_for_duplicates():
    """Test check_for_duplicates function."""
    # Test with no duplicates
    fields = [
        OrderByField(name="name", direction=Direction.ASC),
        OrderByField(name="age", direction=Direction.DESC),
    ]
    # Should not raise an exception
    check_for_duplicates(fields)

    # Test with duplicates
    fields = [
        OrderByField(name="name", direction=Direction.ASC),
        OrderByField(name="name", direction=Direction.DESC),
    ]
    # Should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        check_for_duplicates(fields)
    assert "Conflicting order_by parameters detected: name" in str(exc_info.value)


def test_validate_order_by_query_params():
    """Test validate_order_by_query_params function."""
    # Create a test enum
    TestEnum = create_order_by_enum(["name", "age"])

    # Test with valid parameters
    fields = validate_order_by_query_params({TestEnum["+name"], TestEnum["-age"]})
    assert len(fields) == 2

    # Check that the fields are validated correctly
    name_field = next(f for f in fields if f.name == "name")
    age_field = next(f for f in fields if f.name == "age")
    assert name_field.direction == Direction.ASC
    assert age_field.direction == Direction.DESC

    # Test with conflicting parameters
    with pytest.raises(ValueError) as exc_info:
        validate_order_by_query_params({TestEnum["+name"], TestEnum["-name"]})
    assert "Conflicting order_by parameters detected: name" in str(exc_info.value)
