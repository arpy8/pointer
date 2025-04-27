"""System command services"""

import time
import webbrowser
import threading
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type

from app.utils.logger import get_logger
from app.utils.config import settings
from app.utils.system import run_system_command
from app.services.keyboard import press_button_combination, press_sequence

logger = get_logger("commands")

class CommandHandler(ABC):
    """Base class for command handlers"""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command"""
        pass

class ShutdownHandler(CommandHandler):
    """Handle system shutdown command"""
    
    def execute(self) -> None:
        try:
            press_button_combination("win-m")
            time.sleep(0.2)
            press_button_combination("alt-f4")
            time.sleep(0.2)
            press_button_combination("enter")
            logger.info("Shutdown command executed")
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            raise

class SleepHandler(CommandHandler):
    """Handle system sleep command"""
    
    def execute(self) -> None:
        try:
            press_button_combination("win-m")
            time.sleep(0.2)
            press_button_combination("alt-f4")
            time.sleep(0.2)

            press_sequence(["down"] * 5)
            press_sequence(["up"] * 2)
            press_button_combination("enter")
            logger.info("Sleep command executed")
        except Exception as e:
            logger.error(f"Sleep command failed: {e}")
            raise

class BSODHandler(CommandHandler):
    """Handle BSOD simulation command"""
    
    def execute(self) -> None:
        try:
            result = run_system_command(['bsod'])
            logger.info(f"BSOD command executed with return code {result.returncode}")
            if result.returncode != 0:
                logger.warning(f"BSOD command stderr: {result.stderr}")
        except Exception as e:
            logger.error(f"BSOD command failed: {e}")
            raise

class VolumeHandler(CommandHandler):
    """Handle volume adjustment commands"""
    
    def __init__(self, direction: str):
        """
        Initialize volume handler
        
        Args:
            direction: Either "up" or "down"
        """
        self.direction = direction
        
    def execute(self) -> None:
        try:
            key = "volumeup" if self.direction == "up" else "volumedown"
            press_sequence([key] * 10, interval=0.01)
            logger.info(f"Volume {self.direction} command executed")
        except Exception as e:
            logger.error(f"Volume {self.direction} command failed: {e}")
            raise

class OpenWebsiteHandler(CommandHandler):
    """Handle website opening commands"""
    
    def __init__(self, site: str):
        """
        Initialize website handler
        
        Args:
            site: Website key from settings.URLS
        """
        self.site = site
        
    def execute(self) -> None:
        try:
            if self.site not in settings.URLS:
                raise ValueError(f"Unknown website: {self.site}")
                
            threading.Thread(
                target=webbrowser.open,
                args=(settings.URLS[self.site],)
            ).start()
            logger.info(f"Opened {self.site} in browser")
        except Exception as e:
            logger.error(f"Failed to open {self.site}: {e}")
            raise

class OpenCameraHandler(CommandHandler):
    """Handle camera opening command"""
    
    def execute(self) -> None:
        try:
            run_system_command(
                ["start", "microsoft.windows.camera:", settings.CAMERA_PATH], 
                shell=True
            )
            logger.info("Opened camera")
        except Exception as e:
            logger.error(f"Failed to open camera: {e}")
            raise

_COMMAND_HANDLERS: Dict[str, Type[CommandHandler]] = {
    "shutdown": ShutdownHandler,
    "sleep": SleepHandler,
    "bsod": BSODHandler,
}

def get_command_handler(command: str) -> Optional[CommandHandler]:
    """
    Get handler for a specific command
    
    Args:
        command: Command identifier
        
    Returns:
        CommandHandler or None if not found
    """
    if command == "volume-up":
        return VolumeHandler("up")
    elif command == "volume-down":
        return VolumeHandler("down")
    elif command == "open-spotify":
        return OpenWebsiteHandler("spotify")
    elif command == "open-youtube":
        return OpenWebsiteHandler("youtube")
    elif command == "open-camera":
        return OpenCameraHandler()
    
    handler_class = _COMMAND_HANDLERS.get(command)
    if handler_class:
        return handler_class()
    
    return None