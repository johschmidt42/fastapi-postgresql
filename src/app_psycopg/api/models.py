import json
from datetime import datetime
from typing import Optional, Annotated, Type
from uuid import uuid4

from pydantic import (
    BaseModel,
    computed_field,
    field_serializer,
    StringConstraints,
    Field,
    UUID4,
    model_validator,
)


class BasePatch(BaseModel):
    """
    A base Pydantic model for PATCH requests.
    It includes a validator to ensure at least one field is provided in the request
    and sets extra='forbid' by default.
    """

    model_config = {
        "extra": "forbid",
    }

    @model_validator(mode="after")
    def _check_at_least_one_field_is_set(self):
        """
        Validates that at least one field was provided in the request data.
        `self.model_fields_set` contains the names of fields that were explicitly set in the input.
        """
        if not self.model_fields_set:
            # Dynamically create a list of field names for the current model
            field_names: str = ", ".join(
                f"'{field_name}'" for field_name in self.model_fields.keys()
            )

            error_message = f"At least one of the following fields must be provided for an update: {field_names}."

            raise ValueError(error_message)
        return self


# Profession

ProfessionName: Type = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]


class ProfessionInput(BaseModel):
    name: ProfessionName

    @computed_field
    def id(self) -> UUID4:
        return uuid4()


class ProfessionUpdate(BaseModel):
    name: ProfessionName


class Profession(BaseModel):
    id: UUID4
    name: ProfessionName


# User

UserName: Type = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_upper=True, min_length=1, max_length=20
    ),
]


class UserInput(BaseModel):
    name: UserName
    profession_id: UUID4

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserUpdate(BaseModel):
    name: UserName
    profession_id: UUID4

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class UserPatch(BasePatch):
    name: Optional[UserName] = None
    profession_id: Optional[UUID4] = None

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class User(BaseModel):
    id: UUID4
    name: UserName
    created_at: datetime
    last_updated_at: Optional[datetime] = None
    profession: Profession


# Order

OrderAmount: Type = Annotated[
    float, Field(strict=True, gt=0, le=1_000_000, decimal_places=2)
]


class OrderInput(BaseModel):
    amount: OrderAmount
    payer_id: UUID4
    payee_id: UUID4

    @computed_field
    def id(self) -> UUID4:
        return uuid4()


class Order(BaseModel):
    id: UUID4
    amount: OrderAmount
    payer: User
    payee: User


# Document

NonEmptyDict: Type = Annotated[dict, Field(min_length=1)]


class DocumentInput(BaseModel):
    document: NonEmptyDict

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()

    @field_serializer("document")
    def serialize_document(self, document: dict, _info) -> str:
        return json.dumps(document)


class DocumentUpdate(BaseModel):
    document: NonEmptyDict

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()

    @field_serializer("document")
    def serialize_document(self, document: dict, _info) -> str:
        return json.dumps(document)


class Document(BaseModel):
    id: UUID4
    document: NonEmptyDict
    created_at: datetime
    last_updated_at: Optional[datetime] = None
