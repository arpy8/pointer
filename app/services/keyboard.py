"""Keyboard control services"""

import time
from typing import List

try:
    import pyautogui as pg
except ImportError:
    raise ImportError("pyautogui is required for keyboard control")

from app.utils.logger import get_logger

logger = get_logger("keyboard")

def press_button_combination(button_combo: str) -> None:
    """
    Press a key or combination of keys
    
    Args:
        button_combo: Single key or hyphen-separated key combination
    """
    if "-" in button_combo:
        keys = button_combo.split("-")
        logger.info(f"Pressing hotkey combination: {keys}")
        pg.hotkey(*keys)
    else:
        logger.info(f"Pressing key: {button_combo}")
        pg.press(button_combo)

def press_sequence(keys: List[str], interval: float = 0.05) -> None:
    """
    Press a sequence of keys with a delay
    
    Args:
        keys: List of keys to press in sequence
        interval: Time between key presses in seconds
    """
    for key in keys:
        pg.press(key, interval=interval)
        
def press_and_hold(key: str, duration: float) -> None:
    """
    Press and hold a key for a duration
    
    Args:
        key: Key to press and hold
        duration: Duration to hold in seconds
    """
    pg.keyDown(key)
    time.sleep(duration)
    pg.keyUp(key)
