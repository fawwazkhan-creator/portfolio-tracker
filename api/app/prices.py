from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .cache import Cache
from .models import Price


def _key(symbol: str) -> str:
    return f"price:{symbol}"


class PriceService:
    def __init__(self, session: Session, cache: Cache, ttl_seconds: int) -> None:
        self._session = session
        self._cache = cache
        self._ttl = ttl_seconds

    def latest(self, symbols: Iterable[str]) -> dict[str, Decimal]:
        found: dict[str, Decimal] = {}
        missing: list[str] = []
        for symbol in set(symbols):
            cached = self._cache.get(_key(symbol))
            if cached is None:
                missing.append(symbol)
            else:
                found[symbol] = Decimal(cached)
        if missing:
            rows = self._session.scalars(select(Price).where(Price.symbol.in_(missing))).all()
            for row in rows:
                found[row.symbol] = row.price
                self._cache.set(_key(row.symbol), str(row.price), self._ttl)
        return found

    def all(self) -> list[Price]:
        return list(self._session.scalars(select(Price).order_by(Price.symbol)).all())

    def set(self, symbol: str, price: Decimal) -> Price:
        row = self._session.get(Price, symbol)
        if row is None:
            row = Price(symbol=symbol, price=price)
            self._session.add(row)
        else:
            row.price = price
        self._session.commit()
        self._session.refresh(row)
        self._cache.delete(_key(symbol))
        return row
