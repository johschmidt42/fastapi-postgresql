import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, computed_field, ConfigDict, field_serializer


# User


class UserInput(BaseModel):
    name: str

    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserUpdate(BaseModel):
    name: str

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class UserResponseModel(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Order


class OrderInput(BaseModel):
    amount: float
    payer_id: str
    payee_id: str

    @computed_field
    def id(self) -> str:
        return uuid4().hex


class OrderResponseModel(BaseModel):
    id: str
    amount: float
    payer: UserResponseModel
    payee: UserResponseModel

    model_config = ConfigDict(from_attributes=True)


# Document


class DocumentInput(BaseModel):
    document: dict

    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()

    @field_serializer("document")
    def serialize_document(self, document: dict, _info) -> str:
        return json.dumps(document)


class DocumentUpdate(BaseModel):
    document: dict

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()

    @field_serializer("document")
    def serialize_document(self, document: dict, _info) -> str:
        return json.dumps(document)


class DocumentResponseModel(BaseModel):
    id: str
    document: dict
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
