from typing import Generic, TypeVar, Sequence

from pydantic import conint, BaseModel, Field

DataT: TypeVar = TypeVar("DataT")


class LimitOffsetPage(BaseModel, Generic[DataT]):
    items: Sequence[DataT]
    items_count: conint(ge=0)
    total_count: conint(ge=0)
    limit: conint(ge=1, le=50)
    offset: conint(ge=0, le=1000)


class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=50)
    offset: int = Field(0, ge=0, le=1000)
