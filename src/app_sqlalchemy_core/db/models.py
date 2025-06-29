from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    String,
    TIMESTAMP,
    Numeric,
    CheckConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID

from app_sqlalchemy_core.db import metadata

from sqlalchemy.dialects.postgresql import JSONB

professions: Table = Table(
    "professions",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("last_updated_at", TIMESTAMP, nullable=True),
)

companies: Table = Table(
    "companies",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("last_updated_at", TIMESTAMP, nullable=True),
)

users: Table = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String(20), nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("last_updated_at", TIMESTAMP, nullable=True),
    Column("profession_id", UUID, ForeignKey("professions.id"), nullable=False),
)

users_companies: Table = Table(
    "users_companies",
    metadata,
    Column(
        "user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "company_id",
        UUID,
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("created_at", TIMESTAMP, nullable=False),
)

orders: Table = Table(
    "orders",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("amount", Numeric(9, 2), nullable=False),
    Column("payer_id", UUID, ForeignKey("users.id"), nullable=False),
    Column("payee_id", UUID, ForeignKey("users.id"), nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    CheckConstraint("amount >= 0 AND amount <= 1000000", name="amount_check"),
)

documents: Table = Table(
    "documents",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("document", JSON().with_variant(JSONB, "postgresql"), nullable=True),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("last_updated_at", TIMESTAMP, nullable=True),
    Column("user_id", UUID, ForeignKey("users.id"), nullable=False),
)
