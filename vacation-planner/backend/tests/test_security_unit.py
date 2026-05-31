import asyncio

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core import security


def test_verify_token_accepts_valid_hs_token(monkeypatch):
    secret = "test-secret-that-is-long-enough"
    monkeypatch.setattr(security, "_HMAC_SECRET", secret)
    token = jwt.encode({"sub": "user-123"}, secret, algorithm="HS256")

    assert asyncio.run(security.verify_token(token)) == "user-123"


def test_verify_token_rejects_missing_subject(monkeypatch):
    secret = "test-secret-that-is-long-enough"
    monkeypatch.setattr(security, "_HMAC_SECRET", secret)
    token = jwt.encode({"email": "traveler@example.com"}, secret, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(security.verify_token(token))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Missing user ID."


def test_verify_token_rejects_invalid_signature(monkeypatch):
    monkeypatch.setattr(security, "_HMAC_SECRET", "correct-secret")
    token = jwt.encode({"sub": "user-123"}, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(security.verify_token(token))

    assert exc.value.status_code == 401
    assert "Invalid token" in exc.value.detail
