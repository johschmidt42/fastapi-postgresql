import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Annotated, Dict

from sqlalchemy import Column, ForeignKey, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, TIMESTAMP, Numeric

from app_sqlalchemy_orm.db import Base

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
]
required_str_50 = Annotated[str, mapped_column(String(50), nullable=False)]
required_str_20 = Annotated[str, mapped_column(String(20), nullable=False)]

created_at_type = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=lambda: datetime.now(),
    ),
]
updated_at_type = Annotated[
    Optional[datetime],
    mapped_column(
        TIMESTAMP(timezone=False), onupdate=lambda: datetime.now()
    ),
]
user_fk_nn = Annotated[
    uuid.UUID,
    mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
]


# Association table for users and companies
users_companies_table = Table(
    "users_companies",
    Base.metadata,
    Column(
        "user_id",
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "company_id",
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        TIMESTAMP(timezone=False),
        nullable=False,
        default=lambda: datetime.now(),
    ),
)


class Profession(Base):
    __tablename__ = "professions"

    id: Mapped[uuid_pk]
    name: Mapped[required_str_50]
    created_at: Mapped[created_at_type]
    last_updated_at: Mapped[updated_at_type]

    users: Mapped[List["User"]] = relationship(back_populates="profession")

    def __repr__(self) -> str:
        return f"<Profession(id={self.id}, name='{self.name}')>"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid_pk]
    name: Mapped[required_str_50]
    created_at: Mapped[created_at_type]
    last_updated_at: Mapped[updated_at_type]

    users: Mapped[List["User"]] = relationship(
        secondary=users_companies_table, back_populates="companies"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[required_str_20]
    created_at: Mapped[created_at_type]
    last_updated_at: Mapped[updated_at_type]
    profession_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("professions.id"), nullable=False
    )

    profession: Mapped["Profession"] = relationship(back_populates="users")
    companies: Mapped[List["Company"]] = relationship(
        secondary=users_companies_table, back_populates="users"
    )
    orders_placed: Mapped[List["Order"]] = relationship(
        foreign_keys="Order.payer_id", back_populates="payer"
    )
    orders_received: Mapped[List["Order"]] = relationship(
        foreign_keys="Order.payee_id", back_populates="payee"
    )
    documents: Mapped[List["Document"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}')>"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("amount >= 0 AND amount <= 1000000", name="ck_order_amount"),
    )

    id: Mapped[uuid_pk]
    amount: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False)
    # Define the mapped columns for payer_id and payee_id directly
    payer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    payee_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[created_at_type]

    payer: Mapped["User"] = relationship(
        foreign_keys=[payer_id],  # Pass the column object here
        back_populates="orders_placed",
    )
    payee: Mapped["User"] = relationship(
        foreign_keys=[payee_id],  # Pass the column object here
        back_populates="orders_received",
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, amount={self.amount})>"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid_pk]
    document: Mapped[Optional[Dict]] = mapped_column(
        JSONB
    )  # JSONB can store dicts/lists
    created_at: Mapped[created_at_type]
    last_updated_at: Mapped[updated_at_type]
    user_id: Mapped[
        user_fk_nn
    ]  # This uses the Annotated type, which is fine as it wraps mapped_column

    user: Mapped["User"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, user_id='{self.user_id}')>"
