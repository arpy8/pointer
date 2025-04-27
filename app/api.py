"""API endpoints for Remote Control"""

import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse

from app.utils.logger import get_logger
from app.utils.security import check_api_key
from app.services.keyboard import press_button_combination
from app.services.commands import get_command_handler

logger = get_logger("api")

BASE_PATH = Path(__file__).parent.parent
STATIC_PATH = BASE_PATH / "static"
STATIC_PATH.mkdir(exist_ok=True)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    _app = FastAPI(
        title="Remote Control API",
        description="API for remote control of keyboard and system functions",
        version="1.0.0"
    )
    
    _app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

    _app = register_middleware(_app)
    _app = register_exception_handlers(_app)
    
    register_routes(_app)
    
    return _app

def register_middleware(app_instance: FastAPI) -> FastAPI:
    """Register middleware components"""
    
    @app_instance.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log HTTP request information"""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        return response
    
    return app_instance

def register_exception_handlers(app_instance: FastAPI) -> FastAPI:
    """Register exception handlers"""
    
    @app_instance.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unhandled exceptions"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error occurred"}
        )
    
    return app_instance

def register_routes(app_instance: FastAPI) -> None:
    """Register API routes"""
    
    @app_instance.get("/manifest.json")
    def get_manifest():
        """Serve the web app manifest"""
        manifest_path = BASE_PATH / "manifest.json"
        if not manifest_path.exists():
            logger.warning(f"Manifest not found at {manifest_path}")
            raise HTTPException(status_code=404, detail="Manifest not found")
        return FileResponse(manifest_path)

    @app_instance.get("/", response_class=FileResponse)
    async def read_root():
        """Serve the index page"""
        index_path = BASE_PATH / "index.html"
        if not index_path.exists():
            logger.warning(f"Index page not found at {index_path}")
            raise HTTPException(status_code=404, detail="Index page not found")
        return index_path

    @app_instance.get("/press/{button}")
    def press_key(button: str, request: Request):
        """Press keyboard button(s)"""
        try:
            check_api_key(request)
            press_button_combination(button)
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error pressing key {button}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to press key: {str(e)}")

    @app_instance.get("/exec/{command}")
    def exec_command(command: str, request: Request):
        """Execute system command"""
        try:
            check_api_key(request)
            handler = get_command_handler(command)
            if not handler:
                logger.warning(f"Unknown command requested: {command}")
                raise HTTPException(status_code=400, detail=f"Unknown command: {command}")
            
            handler.execute()
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

app = create_app()