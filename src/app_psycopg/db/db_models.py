from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, UUID4, constr, condecimal


class Profession(BaseModel):
    id: UUID4
    name: constr(max_length=50)


class User(BaseModel):
    id: UUID4
    name: constr(max_length=20)
    created_at: datetime
    last_updated_at: Optional[datetime] = None
    profession_id: UUID4


class Order(BaseModel):
    id: UUID4
    amount: condecimal(ge=0, le=1000000, decimal_places=2)
    payer_id: UUID4
    payee_id: UUID4
    payer: Optional[User] = None
    payee: Optional[User] = None


class Document(BaseModel):
    id: UUID4
    document: Dict[str, Any]
    created_at: datetime
    last_updated_at: Optional[datetime] = None
