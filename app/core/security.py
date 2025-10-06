from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name='X-API-KEY', auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):

    if api_key is None or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Missing API key"
        )
    
    return api_key
