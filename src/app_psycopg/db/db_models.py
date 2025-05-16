from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_updated_at: Optional[datetime] = None


class Order(BaseModel):
    id: str
    amount: float
    payer: User
    payee: User


class Document(BaseModel):
    id: str
    document: dict
    created_at: datetime
    last_updated_at: Optional[datetime] = None
