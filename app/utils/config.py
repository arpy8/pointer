"""Application configuration settings"""

import os
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Settings:
    """Application settings"""
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "80"))
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    API_KEY_ENABLED: bool = os.getenv("API_KEY_ENABLED", "False").lower() == "true"
    API_KEY: str = os.getenv("API_KEY", "2907")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    URLS: Dict[str, str] = field(default_factory=lambda: {
        "youtube": "https://www.youtube.com",
        "spotify": "https://open.spotify.com",
    })
    
    CAMERA_PATH: str = "C:\\Windows\\System32\\Camera.exe"

settings = Settings()