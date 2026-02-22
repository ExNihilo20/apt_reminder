import time
import requests
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.settings import get_settings

settings = get_settings()
security = HTTPBearer()

_JWKS_CACHE = None
_JWKS_CACHE_TS = 0
_JWKS_TTL_SECONDS = 3600


def _get_jwks():
    global _JWKS_CACHE, _JWKS_CACHE_TS

    now = time.time()

    # Return cached keys if still valid
    if _JWKS_CACHE and (now - _JWKS_CACHE_TS) < _JWKS_TTL_SECONDS:
        return _JWKS_CACHE

    jwks_url = (
        f"{settings.keycloak_url}/realms/"
        f"{settings.keycloak_realm}/protocol/openid-connect/certs"
    )

    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        _JWKS_CACHE = response.json()
        _JWKS_CACHE_TS = now
        return _JWKS_CACHE
    except Exception:
        # If we already have cached keys, allow system to continue
        if _JWKS_CACHE:
            return _JWKS_CACHE
        raise


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    issuer = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        jwks = _get_jwks()
        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.keycloak_audience,
            issuer=issuer,
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )