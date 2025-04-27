"""Security utilities"""

from fastapi import Request, HTTPException, status

from app.utils.config import settings

def check_api_key(request: Request) -> None:
    """
    Validate API key if enabled
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If API key validation fails
    """
    if not settings.API_KEY_ENABLED:
        return
        
    api_key = request.headers.get(settings.API_KEY_HEADER)
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": settings.API_KEY_HEADER},
        )
