import logging
import time
from typing import Protocol

import redis

log = logging.getLogger("app.cache")


class Cache(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...

    def delete(self, key: str) -> None: ...

    def is_healthy(self) -> bool: ...


class MemoryCache:
    def __init__(self) -> None:
        self._items: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> str | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if time.monotonic() >= expires_at:
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._items[key] = (time.monotonic() + ttl_seconds, value)

    def delete(self, key: str) -> None:
        self._items.pop(key, None)

    def is_healthy(self) -> bool:
        return True


class RedisCache:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    @classmethod
    def from_url(cls, url: str) -> "RedisCache":
        return cls(
            redis.Redis.from_url(url, decode_responses=True, socket_timeout=1, socket_connect_timeout=1)
        )

    def get(self, key: str) -> str | None:
        try:
            return self._client.get(key)
        except redis.RedisError as error:
            log.warning("cache read failed for %s: %s", key, error)
            return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            self._client.set(key, value, ex=ttl_seconds)
        except redis.RedisError as error:
            log.warning("cache write failed for %s: %s", key, error)

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except redis.RedisError as error:
            log.warning("cache delete failed for %s: %s", key, error)

    def is_healthy(self) -> bool:
        try:
            return bool(self._client.ping())
        except redis.RedisError:
            return False


def make_cache(redis_url: str | None) -> Cache:
    return RedisCache.from_url(redis_url) if redis_url else MemoryCache()
