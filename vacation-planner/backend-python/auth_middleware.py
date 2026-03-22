"""
FastAPI auth dependency.
Extracts and verifies the Supabase JWT from the Authorization header.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from loguru import logger

load_dotenv()

SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

# User-provided JWK for ES256 verification (Supabase ECDSA)
SUPABASE_JWK = {
    "x": "vBsf5nvXRkgs1CuYyPju4Q8Z9bihRgbbtwSKjYhI2LM",
    "y": "GwN11KT-uP_kJ31EmkvQD0ZRnzmramWP3CmsTdNYNuQ",
    "alg": "ES256",
    "crv": "P-256",
    "kid": "3e69f652-3dcd-4159-ac91-6a6ac23d0b65",
    "kty": "EC"
}

if not SUPABASE_JWT_SECRET:
    logger.warning("SUPABASE_JWT_SECRET not set — auth will reject all requests.")

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency that:
    1. Extracts the Bearer token from the Authorization header
    2. Decodes & verifies it using Supabase's JWT secret
    3. Returns the user's UUID (sub claim)

    Raises 401 on any failure.
    """
    token = credentials.credentials

    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth not configured (missing JWT secret).",
        )

    try:
        from jose import jwt as jose_jwt
        
        # 1. Log the header to be 100% sure about the 'alg'
        unverified_header = jose_jwt.get_unverified_header(token)
        logger.debug(f"[AUTH] JWT Header: {unverified_header}")
        
        # 2. Log the unverified claims (replacement for get_payload in older python-jose)
        try:
            unverified_claims = jose_jwt.get_unverified_claims(token)
            logger.debug(f"[AUTH] Unverified Claims: {unverified_claims}")
        except Exception:
            logger.debug("[AUTH] Could not extract unverified claims.")

        # 3. Choose the correct key and algorithm based on the header
        alg = unverified_header.get("alg", "HS256")
        kid = unverified_header.get("kid")
        
        verify_key = SUPABASE_JWT_SECRET
        if alg == "ES256" and kid == SUPABASE_JWK["kid"]:
            from jose import jwk
            verify_key = jwk.construct(SUPABASE_JWK)
            logger.debug("[AUTH] Using ES256 public key for verification.")
        else:
            logger.debug(f"[AUTH] Using HMAC secret for {alg} verification.")

        payload = jwt.decode(
            token,
            verify_key,
            algorithms=["HS256", "HS384", "HS512", "ES256"],
            audience=["authenticated", "anon", "service_role"],
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_signature": True
            }
        )
        
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID.",
            )
        
        logger.success(f"[AUTH] User {user_id} verified successfully.")
        return user_id

    except jose_jwt.ExpiredSignatureError:
        logger.warning("[AUTH] Token has expired.")
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
    except (JWTError, jose_jwt.JWKError) as e:
        err_msg = str(e)
        if "algorithm" in err_msg.lower() or "pem" in err_msg.lower():
            logger.error(f"[AUTH] ALGORITHM MISMATCH: Your token uses {unverified_header.get('alg')}, but your SUPABASE_JWT_SECRET is a simple string.")
            logger.error("[AUTH] ACTION REQUIRED: Go to Supabase Dashboard -> Settings -> API -> JWT Settings and set 'JWT Algorithm' to 'HS256'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"JWT Algorithm Mismatch: Expected HS256, got {unverified_header.get('alg')}. Please check Supabase settings.",
            )
        
        logger.error(f"[AUTH] JWT verification failed. Error: {err_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Verification failed: {err_msg}",
        )
