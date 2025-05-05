from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, computed_field
from pydantic import ConfigDict


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

    model_config = ConfigDict(from_attributes=True)

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
