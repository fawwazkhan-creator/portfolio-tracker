import hmac
import re
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .cache import Cache
from .models import Transaction
from .portfolio import OversellError, Trade, build_positions, build_summary, replay
from .prices import PriceService
from .schemas import (
    SYMBOL_PATTERN,
    HealthOut,
    PositionOut,
    PriceIn,
    PriceOut,
    SummaryOut,
    TransactionIn,
    TransactionOut,
)

router = APIRouter(prefix="/api")
SYMBOL_RE = re.compile(SYMBOL_PATTERN)


def get_session(request: Request) -> Iterator[Session]:
    session = request.app.state.db.session()
    try:
        yield session
    finally:
        session.close()


def get_cache(request: Request) -> Cache:
    return request.app.state.cache


def require_api_key(request: Request, x_api_key: Annotated[str | None, Header()] = None) -> None:
    expected = request.app.state.settings.api_key
    if expected and not (x_api_key and hmac.compare_digest(x_api_key, expected)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "A valid X-API-Key header is required")


SessionDep = Annotated[Session, Depends(get_session)]
CacheDep = Annotated[Cache, Depends(get_cache)]


def get_prices(request: Request, session: SessionDep, cache: CacheDep) -> PriceService:
    return PriceService(session, cache, request.app.state.settings.price_cache_seconds)


PricesDep = Annotated[PriceService, Depends(get_prices)]
WriteAccess = Depends(require_api_key)


def _trade(row: Transaction) -> Trade:
    return Trade(row.symbol, row.side, row.quantity, row.price, row.fee, row.executed_at, row.id)


def _all_trades(session: Session, symbol: str | None = None) -> list[Trade]:
    query = select(Transaction)
    if symbol:
        query = query.where(Transaction.symbol == symbol)
    return [_trade(row) for row in session.scalars(query).all()]


@router.get("/health", response_model=HealthOut)
def health(request: Request, response: Response) -> HealthOut:
    database_up = request.app.state.db.is_healthy()
    cache_up = request.app.state.cache.is_healthy()
    if not database_up:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthOut(
        status="ok" if database_up and cache_up else "degraded",
        database="up" if database_up else "down",
        cache="up" if cache_up else "down",
    )


@router.get("/transactions", response_model=list[TransactionOut])
def list_transactions(session: SessionDep, symbol: str | None = None) -> list[Transaction]:
    query = select(Transaction).order_by(Transaction.executed_at.desc(), Transaction.id.desc())
    if symbol:
        query = query.where(Transaction.symbol == symbol.strip().upper())
    return list(session.scalars(query).all())


@router.post(
    "/transactions",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[WriteAccess],
)
def create_transaction(payload: TransactionIn, session: SessionDep) -> Transaction:
    candidate = Trade(
        payload.symbol, payload.side, payload.quantity, payload.price, payload.fee, payload.executed_at
    )
    try:
        replay([*_all_trades(session, payload.symbol), candidate])
    except OversellError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error
    row = Transaction(**payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[WriteAccess],
)
def delete_transaction(transaction_id: int, session: SessionDep) -> Response:
    row = session.get(Transaction, transaction_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")
    remaining = [t for t in _all_trades(session, row.symbol) if t.id != transaction_id]
    try:
        replay(remaining)
    except OversellError as error:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Deleting this transaction would break a later sale. {error}",
        ) from error
    session.delete(row)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/positions", response_model=list[PositionOut])
def positions(session: SessionDep, prices: PricesDep) -> list[PositionOut]:
    holdings = replay(_all_trades(session))
    latest = prices.latest(holdings.keys())
    return [PositionOut.model_validate(p) for p in build_positions(holdings, latest)]


@router.get("/summary", response_model=SummaryOut)
def summary(session: SessionDep, prices: PricesDep) -> SummaryOut:
    holdings = replay(_all_trades(session))
    latest = prices.latest(holdings.keys())
    return SummaryOut.model_validate(build_summary(holdings, latest))


@router.get("/prices", response_model=list[PriceOut])
def list_prices(prices: PricesDep) -> list[PriceOut]:
    return [PriceOut.model_validate(row) for row in prices.all()]


@router.put("/prices/{symbol}", response_model=PriceOut, dependencies=[WriteAccess])
def set_price(symbol: str, payload: PriceIn, prices: PricesDep) -> PriceOut:
    clean = symbol.strip().upper()
    if not SYMBOL_RE.fullmatch(clean):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid symbol")
    return PriceOut.model_validate(prices.set(clean, payload.price))
