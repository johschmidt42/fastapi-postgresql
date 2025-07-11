from pydantic import (
    BaseModel,
    model_validator,
    ConfigDict,
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


class BaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


import json
from datetime import datetime
from decimal import Decimal
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

# region Profession

ProfessionName: Type = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]


class ProfessionInput(BaseInput):
    name: ProfessionName

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class ProfessionUpdate(BaseModel):
    name: ProfessionName

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class Profession(BaseModel):
    id: UUID4
    name: ProfessionName
    created_at: datetime
    last_updated_at: Optional[datetime] = None


class ProfessionShort(BaseModel):
    id: UUID4
    name: ProfessionName


# endregion

# region User

UserName: Type = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_upper=True, min_length=1, max_length=20
    ),
]


class UserInput(BaseInput):
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
    profession: ProfessionShort


class UserShort(BaseModel):
    id: UUID4
    name: UserName


# endregion

# region Order

OrderAmount: Type = Annotated[Decimal, Field(gt=0, le=1_000_000, decimal_places=2)]


class OrderInput(BaseInput):
    amount: OrderAmount
    payer_id: UUID4
    payee_id: UUID4

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()

    @model_validator(mode="after")
    def check_payer_payee_different(self):
        if self.payer_id == self.payee_id:
            raise ValueError("payer_id and payee_id must be different")
        return self


class OrderInputValidated(BaseModel):
    order_input: OrderInput
    payer: User
    payee: User


class Order(BaseModel):
    id: UUID4
    amount: OrderAmount
    payer: UserShort
    payee: UserShort
    created_at: datetime


# endregion

# region Document

NonEmptyDict: Type = Annotated[dict, Field(min_length=1)]


class DocumentInput(BaseInput):
    document: NonEmptyDict
    user_id: UUID4

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
    user_id: UUID4


# endregion

# region Company

CompanyName: Type = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]


class CompanyInput(BaseInput):
    name: CompanyName

    @computed_field
    def id(self) -> UUID4:
        return uuid4()

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class CompanyUpdate(BaseModel):
    name: CompanyName

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class CompanyPatch(BasePatch):
    name: Optional[CompanyName] = None

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class Company(BaseModel):
    id: UUID4
    name: CompanyName
    created_at: datetime
    last_updated_at: Optional[datetime] = None


class CompanyShort(BaseModel):
    id: UUID4
    name: CompanyName


# endregion

# region UserCompanyLink


class UserCompanyLinkInput(BaseInput):
    user_id: UUID4
    company_id: UUID4

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserCompanyLink(BaseModel):
    user_id: UUID4
    company_id: UUID4
    created_at: datetime


class UserCompanyLinkWithCompany(BaseModel):
    user_id: UUID4
    company: CompanyShort
    created_at: datetime


class UserCompanyLinkWithUser(BaseModel):
    company_id: UUID4
    user_info: UserShort
    created_at: datetime


class UserCompanyLinkResponse(BaseModel):
    user_id: UUID4
    company_id: UUID4


# endregion
