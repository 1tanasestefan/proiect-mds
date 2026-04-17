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
from typing import Optional

load_dotenv()

# ── Supabase ECDSA public key (ES256) ────────────────────────────
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

_HMAC_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

async def verify_token(token: str) -> str:
    """
    Core logic to validate a JWT. Returns user_id (sub).
    Raises HTTPException (401) on failure.
    """
    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Malformed token header: {e}")

    alg = header.get("alg", "")
    
    if alg == "ES256":
        if _EC_VERIFY_KEY is None:
            raise HTTPException(status_code=500, detail="ES256 key not configured.")
        verify_key = _EC_VERIFY_KEY
        algorithms = ["ES256"]
    elif alg in ("HS256", "HS384", "HS512"):
        if not _HMAC_SECRET:
            raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET not set.")
        verify_key = _HMAC_SECRET
        algorithms = ["HS256", "HS384", "HS512"]
    else:
        raise HTTPException(status_code=401, detail=f"Unsupported algorithm: {alg}")

    try:
        payload = jwt.decode(
            token,
            verify_key,
            algorithms=algorithms,
            options={"verify_aud": False},
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user ID.")
    
    return user_id

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Strict: Requires a valid token."""
    return await verify_token(credentials.credentials)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
) -> Optional[str]:
    """Optional: Allows guests (returns None) or validates token if present."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await verify_token(credentials.credentials)
    except Exception:
        # If a token was provided but is invalid, we treat them as a guest
        # rather than blocking the whole public page with a 401.
        return None
