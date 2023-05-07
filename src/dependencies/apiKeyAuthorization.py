from fastapi import HTTPException
from fastapi.security import APIKeyHeader
from ..config.config import settings
from fastapi import status, Depends

X_API_KEY = APIKeyHeader(name='X-API-Key', auto_error=True)

class ApiKeyAuthorization():
    async def __call__(self, api_key_header: str = Depends(X_API_KEY)):
        if api_key_header != settings.AuthSettings.XApiKey:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )
        return 