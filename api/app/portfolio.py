import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal("0")
CENT = Decimal("0.01")
PRICE_STEP = Decimal("0.0001")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def percent(part: Decimal, whole: Decimal) -> Decimal | None:
    if whole == ZERO:
        return None
    return (part / whole * 100).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Trade:
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    executed_at: date
    id: int | None = None


class OversellError(ValueError):
    def __init__(self, symbol: str, executed_at: date, requested: Decimal, held: Decimal) -> None:
        self.symbol = symbol
        self.executed_at = executed_at
        self.requested = requested
        self.held = held
        super().__init__(
            f"Cannot sell {requested.normalize():f} {symbol} on {executed_at.isoformat()}: "
            f"only {held.normalize():f} held at that date"
        )


@dataclass
class Holding:
    symbol: str
    quantity: Decimal = ZERO
    cost: Decimal = ZERO
    realized: Decimal = ZERO


@dataclass(frozen=True)
class Position:
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


@dataclass(frozen=True)
class Summary:
    cost_basis: Decimal
    market_value: Decimal
    unrealized_pl: Decimal
    unrealized_pl_pct: Decimal | None
    realized_pl: Decimal
    total_pl: Decimal
    positions_count: int
    unpriced_symbols: list[str] = field(default_factory=list)


def _order(trade: Trade) -> tuple[date, float]:
    return (trade.executed_at, trade.id if trade.id is not None else math.inf)


def replay(trades: Iterable[Trade]) -> dict[str, Holding]:
    holdings: dict[str, Holding] = {}
    for trade in sorted(trades, key=_order):
        holding = holdings.setdefault(trade.symbol, Holding(trade.symbol))
        if trade.side == "buy":
            holding.quantity += trade.quantity
            holding.cost += trade.quantity * trade.price + trade.fee
            continue
        if trade.quantity > holding.quantity:
            raise OversellError(trade.symbol, trade.executed_at, trade.quantity, holding.quantity)
        released = holding.cost / holding.quantity * trade.quantity
        holding.realized += trade.quantity * trade.price - trade.fee - released
        holding.quantity -= trade.quantity
        holding.cost = ZERO if holding.quantity == ZERO else holding.cost - released
    return holdings


def build_positions(holdings: Mapping[str, Holding], prices: Mapping[str, Decimal]) -> list[Position]:
    open_holdings = [h for h in holdings.values() if h.quantity > ZERO]
    values = {
        h.symbol: h.quantity * prices[h.symbol] if h.symbol in prices else h.cost for h in open_holdings
    }
    total_value = sum(values.values(), ZERO)
    positions = []
    for holding in open_holdings:
        price = prices.get(holding.symbol)
        value = values[holding.symbol]
        unrealized = value - holding.cost if price is not None else ZERO
        positions.append(
            Position(
                symbol=holding.symbol,
                quantity=holding.quantity,
                average_cost=(holding.cost / holding.quantity).quantize(PRICE_STEP, rounding=ROUND_HALF_UP),
                cost_basis=money(holding.cost),
                market_price=price,
                market_value=money(value),
                unrealized_pl=money(unrealized),
                unrealized_pl_pct=percent(unrealized, holding.cost) if price is not None else None,
                realized_pl=money(holding.realized),
                allocation_pct=percent(value, total_value),
            )
        )
    return sorted(positions, key=lambda p: (-p.market_value, p.symbol))


def build_summary(holdings: Mapping[str, Holding], prices: Mapping[str, Decimal]) -> Summary:
    positions = build_positions(holdings, prices)
    cost_basis = sum((p.cost_basis for p in positions), ZERO)
    market_value = sum((p.market_value for p in positions), ZERO)
    unrealized = sum((p.unrealized_pl for p in positions), ZERO)
    realized = money(sum((h.realized for h in holdings.values()), ZERO))
    priced_cost = sum((p.cost_basis for p in positions if p.market_price is not None), ZERO)
    return Summary(
        cost_basis=cost_basis,
        market_value=market_value,
        unrealized_pl=unrealized,
        unrealized_pl_pct=percent(unrealized, priced_cost),
        realized_pl=realized,
        total_pl=unrealized + realized,
        positions_count=len(positions),
        unpriced_symbols=sorted(p.symbol for p in positions if p.market_price is None),
    )
