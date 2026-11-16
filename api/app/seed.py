from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from .config import get_settings
from .db import Database
from .models import Price, Transaction

TRADES = [
    ("VOO", "buy", "12", "402.15", "1.50", date(2025, 1, 14)),
    ("AAPL", "buy", "20", "228.40", "1.00", date(2025, 2, 3)),
    ("MSFT", "buy", "8", "409.80", "1.00", date(2025, 3, 11)),
    ("NVDA", "buy", "30", "118.25", "1.00", date(2025, 4, 22)),
    ("AAPL", "sell", "5", "242.10", "1.00", date(2025, 7, 9)),
    ("VOO", "buy", "6", "455.60", "1.50", date(2025, 9, 2)),
    ("GLD", "buy", "10", "312.70", "1.00", date(2025, 10, 6)),
]

PRICES = {"VOO": "498.20", "AAPL": "236.75", "MSFT": "452.30", "NVDA": "141.60", "GLD": "305.40"}


def main() -> None:
    database = Database(get_settings().database_url)
    with database.session() as session:
        if session.scalar(select(func.count()).select_from(Transaction)):
            print("Database already has transactions; nothing seeded.")
            return
        for symbol, side, quantity, price, fee, executed_at in TRADES:
            session.add(
                Transaction(
                    symbol=symbol,
                    side=side,
                    quantity=Decimal(quantity),
                    price=Decimal(price),
                    fee=Decimal(fee),
                    executed_at=executed_at,
                )
            )
        for symbol, price in PRICES.items():
            session.merge(Price(symbol=symbol, price=Decimal(price)))
        session.commit()
    print(f"Seeded {len(TRADES)} transactions and {len(PRICES)} prices (demo data, not live quotes).")


if __name__ == "__main__":
    main()
