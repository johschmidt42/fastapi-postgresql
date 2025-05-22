import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated, Type
from uuid import uuid4

from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    StringConstraints,
    Field,
    model_validator,
    field_serializer,
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


# region Profession

ProfessionName: Type = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]


class ProfessionInput(BaseModel):
    name: ProfessionName

    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class ProfessionUpdate(BaseModel):
    name: ProfessionName

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class ProfessionResponseModel(BaseModel):
    id: str
    name: ProfessionName
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProfessionShortResponseModel(BaseModel):
    id: str
    name: ProfessionName

    model_config = ConfigDict(from_attributes=True)


# endregion


# region User

UserName: Type = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_upper=True, min_length=1, max_length=20
    ),
]


class UserInput(BaseModel):
    name: UserName
    profession_id: str

    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserUpdate(BaseModel):
    name: UserName
    profession_id: str

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class UserPatch(BasePatch):
    name: Optional[UserName] = None
    profession_id: Optional[str] = None

    @computed_field
    def last_updated_at(self) -> datetime:
        return datetime.now()


class UserResponseModel(BaseModel):
    id: str
    name: UserName
    created_at: datetime
    last_updated_at: Optional[datetime] = None
    profession: ProfessionShortResponseModel

    model_config = ConfigDict(from_attributes=True)


class UserShortResponseModel(BaseModel):
    id: str
    name: UserName

    model_config = ConfigDict(from_attributes=True)


# endregion


# region Order

OrderAmount: Type = Annotated[Decimal, Field(gt=0, le=1_000_000, decimal_places=2)]


class OrderInput(BaseModel):
    amount: OrderAmount
    payer_id: str
    payee_id: str

    @computed_field
    def id(self) -> str:
        return uuid4().hex

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
    payer: UserResponseModel
    payee: UserResponseModel


class OrderResponseModel(BaseModel):
    id: str
    amount: OrderAmount
    payer: UserShortResponseModel
    payee: UserShortResponseModel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# endregion


# region Document

NonEmptyDict: Type = Annotated[dict, Field(min_length=1)]


class DocumentInput(BaseModel):
    document: NonEmptyDict
    user_id: str

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
    user_id: str

    model_config = ConfigDict(from_attributes=True)


# endregion


# region Company

CompanyName: Type = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
]


class CompanyInput(BaseModel):
    name: CompanyName

    @computed_field
    def id(self) -> str:
        return uuid4().hex

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


class CompanyResponseModel(BaseModel):
    id: str
    name: CompanyName
    created_at: datetime
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyShortResponseModel(BaseModel):
    id: str
    name: CompanyName

    model_config = ConfigDict(from_attributes=True)


# endregion


# region UserCompanyLink


class UserCompanyLinkInput(BaseModel):
    user_id: str
    company_id: str

    @computed_field
    def created_at(self) -> datetime:
        return datetime.now()


class UserCompanyLinkResponseModel(BaseModel):
    user_id: str
    company_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCompanyLinkWithCompanyResponseModel(BaseModel):
    user_id: str
    company: CompanyShortResponseModel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCompanyLinkWithUserResponseModel(BaseModel):
    company_id: str
    user_info: UserShortResponseModel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCompanyLinkCreatedResponseModel(BaseModel):
    user_id: str
    company_id: str

    model_config = ConfigDict(from_attributes=True)


# endregion
