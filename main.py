import time
import uvicorn
import logging
from pathlib import Path

from app.api import create_app
from app.utils.system import get_local_ip
from app.utils.config import settings
from app.utils.logger import setup_logging, colored

# Setup logging
logger = setup_logging()

def main():
    """Application entry point"""
    # Display IP information for easier connection
    ip_info = get_local_ip()
    if ip_info:
        print(colored(ip_info, "green"), end="\n" * 3)
    else:
        print(colored("Could not determine local IP address", "red"), end="\n" * 3)
    
    # Display server information
    print(colored(f"Starting server at http://{settings.HOST}:{settings.PORT}", "blue"))

    try:
        # Create and run the FastAPI application
        uvicorn.run(
            "app.api:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(colored(f"Server failed to start: {e}", "red"))

if __name__ == "__main__":
    main()