from enum import StrEnum, Enum
from typing import List, Set

from pydantic import BaseModel


def create_order_by_enum(values: List[str]) -> StrEnum:
    """
    Converts a list of strings into a StrEnum with "+" and "-" prefixes,
    providing ascending and descending options.

    Args:
        values (List[str]): A list of field names.

    Returns:
        StrEnum: An enumeration containing each field name prefixed with "+" and "-".
    """

    return StrEnum(
        value="StrEnum", names=[f"+{v}" for v in values] + [f"-{v}" for v in values]
    )


class Direction(str, Enum):
    ASC = "+"
    DESC = "-"


class OrderByField(BaseModel):
    name: str
    direction: Direction


def _parse_str_order_by(name: StrEnum) -> OrderByField:
    return OrderByField(name=name.value[1:], direction=Direction(name.value[0]))


def parse_order_by(order_by: Set[StrEnum]) -> List[OrderByField]:
    return [_parse_str_order_by(ob) for ob in order_by]


def check_for_duplicates(fields: List[OrderByField]):
    """
    Ensures no field is sorted in both ascending and descending order.

    Args:
        fields (List[OrderByField]): A list of parsed order_by fields.

    Raises:
        ValueError: If conflicting sorting directions for the same field are detected.
    """

    field_names: List[str] = [field.name for field in fields]
    duplicates: Set[str] = {name for name in field_names if field_names.count(name) > 1}

    if duplicates:
        raise ValueError(
            f"Conflicting order_by parameters detected: {', '.join(duplicates)}. A field cannot be sorted in both ascending and descending order."
        )


def validate_order_by_query_params(order_by: Set[StrEnum]) -> List[OrderByField]:
    """
    Validates the order_by query parameters and checks for conflicting sorting directions.

    Args:
        order_by (Set[StrEnum]): A set of order_by parameters.

    Returns:
        List[OrderByField]: A list of validated order_by fields.

    Raises:
        ValueError: If a field is sorted in both ascending and descending order.
    """

    fields: List[OrderByField] = parse_order_by(order_by=order_by)

    check_for_duplicates(fields)

    return fields
