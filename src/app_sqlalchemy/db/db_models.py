from sqlalchemy import DECIMAL, String, ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app_sqlalchemy.db import Base


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
