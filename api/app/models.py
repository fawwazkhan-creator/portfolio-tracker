from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("side IN ('buy', 'sell')", name="ck_transactions_side"),
        CheckConstraint("quantity > 0", name="ck_transactions_quantity_positive"),
        CheckConstraint("price > 0", name="ck_transactions_price_positive"),
        CheckConstraint("fee >= 0", name="ck_transactions_fee_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(12), index=True)
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("0"))
    executed_at: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (CheckConstraint("price > 0", name="ck_prices_price_positive"),)

    symbol: Mapped[str] = mapped_column(String(12), primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
