"""System utilities"""

import subprocess
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger("system")

def get_local_ip() -> Optional[str]:
    """
    Get local IP address
    
    Returns:
        Optional[str]: The local IP address string or None if not found
    """
    try:
        result = subprocess.run(
            ['ipconfig'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
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

def run_system_command(command: str, shell: bool = False) -> subprocess.CompletedProcess:
    """
    Run a system command safely
    
    Args:
        command: Command string or list to execute
        shell: Whether to use shell execution
        
    Returns:
        CompletedProcess: Result of the command execution
    """
    try:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            shell=shell
        )
    except Exception as e:
        logger.error(f"Failed to execute system command: {e}")
        raise
