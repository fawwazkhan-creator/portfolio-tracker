from datetime import date
from decimal import Decimal

import pytest

from app.portfolio import OversellError, Trade, build_positions, build_summary, replay

D = Decimal


def trade(symbol, side, quantity, price, day, fee="0", id=None):
    return Trade(symbol, side, D(quantity), D(price), D(fee), date.fromisoformat(day), id)


def test_average_cost_includes_fees():
    holdings = replay(
        [
            trade("AAPL", "buy", "10", "100", "2025-01-01", fee="5", id=1),
            trade("AAPL", "buy", "10", "120", "2025-02-01", fee="5", id=2),
        ]
    )
    holding = holdings["AAPL"]
    assert holding.quantity == D("20")
    assert holding.cost == D("2210")


def test_partial_sale_realises_profit_against_average_cost():
    holdings = replay(
        [
            trade("AAPL", "buy", "10", "100", "2025-01-01", id=1),
            trade("AAPL", "buy", "10", "120", "2025-02-01", id=2),
            trade("AAPL", "sell", "5", "130", "2025-03-01", fee="2", id=3),
        ]
    )
    holding = holdings["AAPL"]
    assert holding.quantity == D("15")
    assert holding.cost == D("1650")
    assert holding.realized == D("98")


def test_full_exit_resets_cost_and_keeps_realised():
    holdings = replay(
        [
            trade("MSFT", "buy", "3", "300", "2025-01-01", id=1),
            trade("MSFT", "sell", "3", "250", "2025-02-01", id=2),
        ]
    )
    assert holdings["MSFT"].quantity == 0
    assert holdings["MSFT"].cost == 0
    assert holdings["MSFT"].realized == D("-150")


def test_trades_replay_in_date_order_not_insert_order():
    holdings = replay(
        [
            trade("NVDA", "sell", "2", "150", "2025-03-01", id=1),
            trade("NVDA", "buy", "5", "100", "2025-01-01", id=2),
        ]
    )
    assert holdings["NVDA"].quantity == D("3")


def test_selling_more_than_held_on_that_date_fails():
    with pytest.raises(OversellError) as error:
        replay(
            [
                trade("NVDA", "buy", "5", "100", "2025-03-01", id=1),
                trade("NVDA", "sell", "2", "150", "2025-01-01", id=2),
            ]
        )
    assert error.value.held == 0
    assert "only 0 held" in str(error.value)


def test_new_trade_on_same_day_is_applied_after_existing_ones():
    holdings = replay(
        [
            trade("VOO", "buy", "4", "400", "2025-05-05", id=7),
            trade("VOO", "sell", "4", "410", "2025-05-05"),
        ]
    )
    assert holdings["VOO"].quantity == 0


def test_positions_value_unrealised_and_allocation():
    holdings = replay(
        [
            trade("AAPL", "buy", "10", "100", "2025-01-01", id=1),
            trade("MSFT", "buy", "1", "300", "2025-01-01", id=2),
        ]
    )
    positions = build_positions(holdings, {"AAPL": D("110"), "MSFT": D("400")})
    assert [p.symbol for p in positions] == ["AAPL", "MSFT"]
    aapl = positions[0]
    assert aapl.market_value == D("1100.00")
    assert aapl.unrealized_pl == D("100.00")
    assert aapl.unrealized_pl_pct == D("10.00")
    assert aapl.allocation_pct == D("73.33")
    assert positions[1].allocation_pct == D("26.67")


def test_unpriced_positions_are_valued_at_cost_and_reported():
    holdings = replay([trade("GLD", "buy", "2", "300", "2025-01-01", id=1)])
    summary = build_summary(holdings, {})
    assert summary.market_value == D("600.00")
    assert summary.unrealized_pl == 0
    assert summary.unrealized_pl_pct is None
    assert summary.unpriced_symbols == ["GLD"]


def test_summary_combines_realised_and_unrealised():
    holdings = replay(
        [
            trade("AAPL", "buy", "10", "100", "2025-01-01", id=1),
            trade("AAPL", "sell", "4", "150", "2025-02-01", id=2),
        ]
    )
    summary = build_summary(holdings, {"AAPL": D("90")})
    assert summary.cost_basis == D("600.00")
    assert summary.market_value == D("540.00")
    assert summary.unrealized_pl == D("-60.00")
    assert summary.realized_pl == D("200.00")
    assert summary.total_pl == D("140.00")
    assert summary.unrealized_pl_pct == D("-10.00")


def test_money_rounding_is_half_up():
    holdings = replay([trade("X", "buy", "3", "0.335", "2025-01-01", id=1)])
    positions = build_positions(holdings, {"X": D("0.3350")})
    assert positions[0].cost_basis == D("1.01")
