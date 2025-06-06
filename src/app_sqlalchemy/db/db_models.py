from sqlalchemy import DECIMAL, String, ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_sqlalchemy.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    last_updated_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    last_updated_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)

    payer_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id"), nullable=False
    )
    payee_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id"), nullable=False
    )

    payer: Mapped["User"] = relationship("User", foreign_keys=payer_id, uselist=False)
    payee: Mapped["User"] = relationship("User", foreign_keys=payee_id, uselist=False)
