"""
FastAPI auth dependency — Supabase JWT verification.

Supabase signs tokens with ES256 (ECDSA P-256) by default.
We verify using the project's ECDSA public JWK via jose.jwk.construct().
HS256 is supported as an optional fallback.
"""

import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError, jwk
from loguru import logger

load_dotenv()

# ── Supabase ECDSA public key (ES256) ────────────────────────────
# This is the PUBLIC half of Supabase's signing key — safe to embed.
# Source: Supabase Dashboard → Settings → API → JWT Settings
_SUPABASE_JWK = {
    "kty": "EC",
    "crv": "P-256",
    "alg": "ES256",
    "kid": "3e69f652-3dcd-4159-ac91-6a6ac23d0b65",
    "x":   "vBsf5nvXRkgs1CuYyPju4Q8Z9bihRgbbtwSKjYhI2LM",
    "y":   "GwN11KT-uP_kJ31EmkvQD0ZRnzmramWP3CmsTdNYNuQ",
}

try:
    _EC_VERIFY_KEY = jwk.construct(_SUPABASE_JWK)
    logger.info("[AUTH] ES256 public key loaded at startup.")
except Exception as _e:
    _EC_VERIFY_KEY = None
    logger.error(f"[AUTH] Could not load ES256 key: {_e}")

# HS256 fallback (only used if the token's alg is HS256)
_HMAC_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Validates a Supabase JWT and returns the authenticated user UUID (sub).
    Supports ES256 (Supabase default) and HS256 (legacy fallback).
    Raises HTTP 401 on any failure.
    """
    token = credentials.credentials

    # Peek at the header without validating yet
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Malformed token header: {e}")

    alg = header.get("alg", "")
    logger.debug(f"[AUTH] Incoming token: alg={alg}, kid={header.get('kid', 'n/a')[:16]}")

    # Select the correct verification key
    if alg == "ES256":
        if _EC_VERIFY_KEY is None:
            raise HTTPException(status_code=500, detail="ES256 key not configured on server.")
        verify_key = _EC_VERIFY_KEY
        algorithms = ["ES256"]
    elif alg in ("HS256", "HS384", "HS512"):
        if not _HMAC_SECRET:
            raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET not set for HS256.")
        verify_key = _HMAC_SECRET
        algorithms = ["HS256", "HS384", "HS512"]
    else:
        logger.error(f"[AUTH] Unsupported algorithm: {alg}")
        raise HTTPException(status_code=401, detail=f"Unsupported token algorithm: {alg}")

    # Decode + verify
    try:
        payload = jwt.decode(
            token,
            verify_key,
            algorithms=algorithms,
            options={"verify_aud": False},
        )
    except ExpiredSignatureError:
        logger.warning("[AUTH] Token expired.")
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except JWTError as e:
        logger.error(f"[AUTH] JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID.")

    logger.debug(f"[AUTH] ✅ User {user_id} authenticated via {alg}")
    return user_id
