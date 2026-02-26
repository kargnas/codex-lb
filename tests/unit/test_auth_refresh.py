from __future__ import annotations

import asyncio
from datetime import timedelta

import aiohttp
import pytest

from app.core.auth.refresh import (
    RefreshError,
    classify_refresh_error,
    is_transient_error,
    refresh_access_token,
    should_refresh,
)
from app.core.utils.time import utcnow

pytestmark = pytest.mark.unit


def test_should_refresh_after_interval():
    last = utcnow() - timedelta(days=9)
    assert should_refresh(last) is True


def test_should_refresh_within_interval():
    last = utcnow() - timedelta(days=1)
    assert should_refresh(last) is False


def test_classify_refresh_error_permanent():
    assert classify_refresh_error("refresh_token_expired") is True


def test_classify_refresh_error_temporary():
    assert classify_refresh_error("temporary_error") is False


def test_is_transient_error_timeout():
    """Timeout errors should be classified as transient."""
    error = RefreshError("timeout", "Token refresh timed out", False)
    assert is_transient_error(error) is True
    assert error.is_permanent is False


def test_is_transient_error_network():
    """Network errors should be classified as transient."""
    error = RefreshError("network_error", "Network error: ClientConnectorError", False)
    assert is_transient_error(error) is True
    assert error.is_permanent is False


def test_is_transient_error_permanent():
    """Permanent errors should NOT be classified as transient."""
    error = RefreshError("refresh_token_expired", "Refresh token expired", True)
    assert is_transient_error(error) is False
    assert error.is_permanent is True


@pytest.mark.asyncio
async def test_refresh_access_token_timeout_is_transient(monkeypatch):
    """Timeout during token refresh should raise RefreshError with is_permanent=False."""
    async def _fake_post_timeout(*args, **kwargs):
        raise asyncio.TimeoutError()

    class _FakeSession:
        def post(self, *args, **kwargs):
            return _FakeContextManager(_fake_post_timeout(*args, **kwargs))

    class _FakeContextManager:
        def __init__(self, coro):
            self._coro = coro
        async def __aenter__(self):
            return await self._coro
        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr("app.core.auth.refresh.get_http_client", lambda: type("obj", (), {"session": _FakeSession()}))

    with pytest.raises(RefreshError) as exc_info:
        await refresh_access_token("dummy-refresh-token")

    assert exc_info.value.code == "timeout"
    assert exc_info.value.is_permanent is False


@pytest.mark.asyncio
async def test_refresh_access_token_network_error_is_transient(monkeypatch):
    """Network error during token refresh should raise RefreshError with is_permanent=False."""
    # Use a simple ClientError subclass that doesn't require complex constructor args
    class _TestNetworkError(aiohttp.ClientError):
        pass

    async def _fake_post_network_error(*args, **kwargs):
        raise _TestNetworkError("Connection failed")

    class _FakeSession:
        def post(self, *args, **kwargs):
            return _FakeContextManager(_fake_post_network_error(*args, **kwargs))

    class _FakeContextManager:
        def __init__(self, coro):
            self._coro = coro
        async def __aenter__(self):
            return await self._coro
        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr("app.core.auth.refresh.get_http_client", lambda: type("obj", (), {"session": _FakeSession()}))

    with pytest.raises(RefreshError) as exc_info:
        await refresh_access_token("dummy-refresh-token")

    assert exc_info.value.code == "network_error"
    assert exc_info.value.is_permanent is False
