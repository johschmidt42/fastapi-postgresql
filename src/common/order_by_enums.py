from typing import Annotated, List, Type, Optional, Set

from pydantic import AfterValidator

from common.sorting import create_order_by_enum, validate_order_by_query_params

company_sortable_fields: List[str] = ["name", "created_at", "last_updated_at"]
OrderByCompany: Type = Annotated[
    Optional[Set[create_order_by_enum(company_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]

document_sortable_fields: List[str] = ["created_at", "last_updated_at"]
OrderByDocument: Type = Annotated[
    Optional[Set[create_order_by_enum(document_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]

order_sortable_fields: List[str] = [
    "amount",
]
OrderByOrder: Type = Annotated[
    Optional[Set[create_order_by_enum(order_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]

profession_sortable_fields: List[str] = ["name"]
OrderByProfession: Type = Annotated[
    Optional[Set[create_order_by_enum(profession_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]

user_sortable_fields: List[str] = [
    "name",
    "created_at",
    "last_updated_at",
]
OrderByUser: Type = Annotated[
    Optional[Set[create_order_by_enum(user_sortable_fields)]],
    AfterValidator(validate_order_by_query_params),
]
