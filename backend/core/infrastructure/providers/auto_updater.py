"""
Auto-updater utility for manual LiteLLM updates.
Includes internet connectivity checks and graceful fallbacks.
"""

import subprocess
import sys
import logging
import socket
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def check_internet_connectivity(timeout: int = 5) -> bool:
    """
    Check if internet connectivity is available.
    
    Args:
        timeout: Connection timeout in seconds
        
    Returns:
        True if internet is available, False otherwise
    """
    try:
        # Try to connect to a reliable host
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except (socket.timeout, socket.error, OSError):
        try:
            # Fallback: try another reliable host
            socket.create_connection(("1.1.1.1", 53), timeout=timeout)
            return True
        except (socket.timeout, socket.error, OSError):
            return False

def get_package_version(package_name: str) -> Optional[str]:
    """
    Get the currently installed version of a package.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        Version string if package is installed, None otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return None

def update_package(package_name: str, silent: bool = True) -> Tuple[bool, str]:
    """
    Update a specific package using pip.
    
    Args:
        package_name: Name of the package to update
        silent: Whether to suppress output
        
    Returns:
        Tuple of (success, message)
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        if silent:
            cmd.append("--quiet")
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout for package updates
        )
        
        if result.returncode == 0:
            return True, f"Successfully updated {package_name}"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, f"Failed to update {package_name}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return False, f"Update of {package_name} timed out"
    except Exception as e:
        return False, f"Error updating {package_name}: {str(e)}"

def force_update_litellm() -> str:
    """
    Force update LiteLLM package only to avoid conflicts.
    
    Returns:
        Status message with results
    """
    if not check_internet_connectivity():
        return "No internet connectivity - cannot update LiteLLM"
    
    current_version = get_package_version("litellm")
    success, message = update_package("litellm", silent=False)
    
    if success:
        new_version = get_package_version("litellm")
        if new_version and new_version != current_version:
            return f"LiteLLM updated: {current_version} -> {new_version}"
        else:
            return f"LiteLLM is already up to date (v{new_version or current_version})"
    else:
        return message  
