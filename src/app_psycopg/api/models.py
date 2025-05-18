import json
from datetime import datetime
from typing import Optional, Annotated, Type
from uuid import uuid4

from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    field_serializer,
    StringConstraints,
    Field,
    UUID4,
)


# User

UserName: Type = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_upper=True, min_length=1, max_length=20
    ),
]


class UserInput(BaseModel):
    name: UserName

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserUpdate(BaseModel):
    name: UserName

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class UserResponseModel(BaseModel):
    id: str
    name: UserName
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Order

OrderAmount: Type = Annotated[
    float, Field(strict=True, gt=0, le=1_000_000, decimal_places=2)
]


class OrderInput(BaseModel):
    amount: OrderAmount
    payer_id: str
    payee_id: str

    @computed_field
    def id(self) -> UUID4:
        return uuid4()


class OrderResponseModel(BaseModel):
    id: str
    amount: OrderAmount
    payer: UserResponseModel
    payee: UserResponseModel

    model_config = ConfigDict(from_attributes=True)


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


class DocumentResponseModel(BaseModel):
    id: str
    document: NonEmptyDict
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
