import time
import uvicorn
import webbrowser
import subprocess
from pathlib import Path
import threading
import logging
from typing import Dict, Callable, Optional, List

try:
    import pyautogui as pg
    from termcolor import colored
    from fastapi import FastAPI, HTTPException, Depends, status, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
    from fastapi.security import APIKeyHeader
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install required packages: pip install fastapi uvicorn pyautogui termcolor")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("remote_control")

# Constants
PORT = 8080
HOST = "0.0.0.0"
API_KEY_NAME = "X-API-Key"
DEFAULT_API_KEY = "1234"

app = FastAPI(
    title="Remote Control API",
    description="API for remote control of keyboard and system functions",
    version="1.0.0"
)

base_path = Path(__file__).parent
static_path = base_path / "static"
static_path.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# def get_api_key(api_key: str = Depends(api_key_header)) -> str:
#     """Validate API key for protected endpoints"""
#     if api_key == DEFAULT_API_KEY:
#         return api_key
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid API Key",
#         headers={"WWW-Authenticate": API_KEY_NAME},
#     )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )

# Routes
@app.get("/favicon.ico")
def get_favicon():
    favicon_path = static_path / "cursor.png"
    if not favicon_path.exists():
        logger.warning(f"Favicon not found at {favicon_path}")
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(favicon_path)

@app.get("/manifest.json")
def get_manifest():
    manifest_path = base_path / "manifest.json"
    if not manifest_path.exists():
        logger.warning(f"Manifest not found at {manifest_path}")
        raise HTTPException(status_code=404, detail="Manifest not found")
    return FileResponse(manifest_path)

@app.get("/", response_class=FileResponse)
async def read_root():
    index_path = base_path / "index.html"
    if not index_path.exists():
        logger.warning(f"Index page not found at {index_path}")
        raise HTTPException(status_code=404, detail="Index page not found")
    return index_path

@app.get("/kbd", response_class=FileResponse)
async def read_keyboard():
    keyboard_path = base_path / "keyboard.html"
    if not keyboard_path.exists():
        logger.warning(f"Keyboard page not found at {keyboard_path}")
        raise HTTPException(status_code=404, detail="Keyboard page not found")
    return keyboard_path

@app.get("/press/{button}")
def press_key(button: str):
    """Press keyboard button(s)"""
    try:
        if "-" in button:
            keys = button.split("-")
            logger.info(f"Pressing hotkey combination: {keys}")
            pg.hotkey(*keys)
        else:
            logger.info(f"Pressing key: {button}")
            pg.press(button)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error pressing key {button}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to press key: {str(e)}")

@app.get("/exec/{command}")
def exec_command(command: str):
    """Execute system command"""
    # Map of commands to functions
    command_functions: Dict[str, Callable] = {
        "shutdown": exec_shutdown,
        "bsod": exec_bsod,
        "sleep": exec_sleep,
        "volume-up": lambda: exec_volume("up"),
        "volume-down": lambda: exec_volume("down"),
        "open-spotify": lambda: exec_open("spotify"),
        "open-youtube": lambda: exec_open("youtube"),
    }
    
    if command not in command_functions:
        logger.warning(f"Unknown command requested: {command}")
        raise HTTPException(status_code=400, detail=f"Unknown command: {command}")
    
    try:
        logger.info(f"Executing command: {command}")
        # Execute the command in a separate thread to avoid blocking
        threading.Thread(target=command_functions[command]).start()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error executing command {command}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

# Helper functions for commands
def exec_shutdown():
    """Shutdown the computer"""
    try:
        pg.hotkey("win", "m")
        time.sleep(0.2)
        pg.hotkey("alt", "f4")
        time.sleep(0.2)
        pg.press("enter")
        logger.info("Shutdown command executed")
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")

def exec_bsod():
    """Simulate Blue Screen of Death"""
    try:
        result = subprocess.run(
            ['bsod'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"BSOD command executed with return code {result.returncode}")
        if result.returncode != 0:
            logger.warning(f"BSOD command stderr: {result.stderr}")
    except Exception as e:
        logger.error(f"BSOD command failed: {e}")

def exec_sleep():
    """Put computer to sleep"""
    try:
        pg.hotkey("win", "m")
        time.sleep(0.2)
        pg.hotkey("alt", "f4")
        time.sleep(0.2)

        for _ in range(5): 
            pg.press("down", interval=0.05)
        for _ in range(2): 
            pg.press("up", interval=0.05)
            
        pg.press("enter")
        logger.info("Sleep command executed")
    except Exception as e:
        logger.error(f"Sleep command failed: {e}")

def exec_volume(state: str):
    """Change system volume"""
    try:
        key = "volumeup" if state == "up" else "volumedown"
        for _ in range(10): 
            pg.press(key)
        logger.info(f"Volume {state} command executed")
    except Exception as e:
        logger.error(f"Volume {state} command failed: {e}")

def exec_open(what: str):
    """Open a website"""
    urls = {
        "youtube": "https://www.youtube.com",
        "spotify": "https://open.spotify.com"
    }
    try:
        if what in urls:
            webbrowser.open(urls[what])
            logger.info(f"Opened {what} in browser")
    except Exception as e:
        logger.error(f"Failed to open {what}: {e}")

def get_local_ip() -> Optional[str]:
    """Get local IP address"""
    try:
        result = subprocess.run(
            ['ipconfig'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.warning(f"ipconfig error: {result.stderr}")
            return None
            
        ip_lines = [line for line in result.stdout.splitlines() if "IPv4 Address" in line]
        if not ip_lines:
            logger.warning("No IPv4 address found")
            return None
            
        return ip_lines[-1].strip()
    except Exception as e:
        logger.error(f"Error getting IP address: {e}")
        return None

def main():
    """Main function"""
    # Get and print IP address
    ip_info = get_local_ip()
    if ip_info:
        print(colored(ip_info, "green"), end="\n" * 3)
    else:
        print(colored("Could not determine local IP address", "red"), end="\n" * 3)
    
    # Show security warning if using default API key
    # if DEFAULT_API_KEY == "1234":
    #     print(colored("WARNING: Using default API key. This is insecure!", "yellow"))
    #     print(colored("Change the DEFAULT_API_KEY value for production use.", "yellow"), end="\n" * 2)
    
    # Start server
    print(colored(f"Starting server at http://{HOST}:{PORT}", "blue"))
    try:
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(colored(f"Server failed to start: {e}", "red"))

if __name__ == "__main__":
    main()