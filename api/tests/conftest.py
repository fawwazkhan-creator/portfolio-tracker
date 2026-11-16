import os
from collections.abc import Iterator

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app.cache import RedisCache
from app.config import Settings
from app.db import Base
from app.main import create_app


@pytest.fixture
def settings(tmp_path) -> Settings:
    url = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{tmp_path / 'test.db'}"
    return Settings(database_url=url, redis_url=None, api_key=None, price_cache_seconds=60)


@pytest.fixture
def cache() -> RedisCache:
    return RedisCache(fakeredis.FakeRedis(decode_responses=True))


@pytest.fixture
def client(settings: Settings, cache: RedisCache) -> Iterator[TestClient]:
    app = create_app(settings, cache=cache)
    engine = app.state.db.engine
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)
    engine.dispose()


def add(client: TestClient, symbol: str, side: str, quantity: str, price: str, day: str, fee: str = "0"):
    return client.post(
        "/api/transactions",
        json={
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "fee": fee,
            "executed_at": day,
        },
    )
