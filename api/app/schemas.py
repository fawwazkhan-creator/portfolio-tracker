from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SYMBOL_PATTERN = r"^[A-Za-z0-9.\-]{1,12}$"


def _clean_symbol(value: str) -> str:
    return value.strip().upper()


class TransactionIn(BaseModel):
    symbol: str = Field(pattern=SYMBOL_PATTERN)
    side: Literal["buy", "sell"]
    quantity: Decimal = Field(gt=0, max_digits=20, decimal_places=6)
    price: Decimal = Field(gt=0, max_digits=20, decimal_places=4)
    fee: Decimal = Field(default=Decimal("0"), ge=0, max_digits=20, decimal_places=4)
    executed_at: date

    @field_validator("symbol", mode="before")
    @classmethod
    def normalise_symbol(cls, value: str) -> str:
        return _clean_symbol(value) if isinstance(value, str) else value

    @field_validator("executed_at")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("executed_at cannot be in the future")
        return value


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    executed_at: date


class PriceIn(BaseModel):
    price: Decimal = Field(gt=0, max_digits=20, decimal_places=4)


class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    price: Decimal
    updated_at: datetime | None


class PositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    quantity: Decimal
    average_cost: Decimal
    cost_basis: Decimal
    market_price: Decimal | None
    market_value: Decimal
    unrealized_pl: Decimal
    unrealized_pl_pct: Decimal | None
    realized_pl: Decimal
    allocation_pct: Decimal | None


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cost_basis: Decimal
    market_value: Decimal
    unrealized_pl: Decimal
    unrealized_pl_pct: Decimal | None
    realized_pl: Decimal
    total_pl: Decimal
    positions_count: int
    unpriced_symbols: list[str]


class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["up", "down"]
    cache: Literal["up", "down"]
