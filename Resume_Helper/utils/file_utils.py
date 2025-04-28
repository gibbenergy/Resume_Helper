"""
Utility functions for file operations with proper locking and atomic writes (cross-platform).
"""

import os
import json
import tempfile
import uuid
import time
import logging
import platform
from typing import Dict, Any, Optional, Tuple

# Conditional imports based on OS
if platform.system() == "Windows":
    import msvcrt
else:
    import fcntl

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileLock:
    def __init__(self, lock_file: str, timeout: int = 10):
        self.lock_file = lock_file
        self.timeout = timeout
        self.fd = None
        self.acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        start_time = time.time()
        if not os.path.exists(self.lock_file):
            open(self.lock_file, 'w').close()

        self.fd = open(self.lock_file, 'r+')

        while True:
            try:
                if platform.system() == "Windows":
                    msvcrt.locking(self.fd.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.acquired = True
                return True
            except (IOError, OSError):
                if time.time() - start_time > self.timeout:
                    logger.warning(f"Timeout waiting for lock: {self.lock_file}")
                    self.fd.close()
                    return False
                time.sleep(0.1)

    def release(self):
        if self.acquired:
            try:
                if platform.system() == "Windows":
                    self.fd.seek(0)
                    msvcrt.locking(self.fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
                self.acquired = False
            except Exception as e:
                logger.error(f"Error releasing lock: {str(e)}")

def atomic_write_json(data: Dict[str, Any], output_path: str) -> Tuple[bool, str]:
    request_id = str(uuid.uuid4())
    logger.info(f"[Request {request_id}] Starting atomic write to {output_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    lock_file = f"{output_path}.lock"

    try:
        with FileLock(lock_file, timeout=30) as lock:
            if not lock.acquired:
                error_msg = f"Could not acquire lock for {output_path}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return False, error_msg

            temp_dir = os.path.dirname(output_path)
            temp_prefix = f".{os.path.basename(output_path)}.tmp"

            with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, prefix=temp_prefix, delete=False) as temp_file:
                temp_path = temp_file.name
                json.dump(data, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            os.replace(temp_path, output_path)
            logger.info(f"[Request {request_id}] Successfully wrote to {output_path}")

            return True, ""
    except Exception as e:
        error_msg = f"Error writing to {output_path}: {str(e)}"
        logger.error(f"[Request {request_id}] {error_msg}")
        return False, error_msg

def atomic_read_json(input_path: str) -> Tuple[Optional[Dict[str, Any]], str]:
    request_id = str(uuid.uuid4())
    logger.info(f"[Request {request_id}] Starting atomic read from {input_path}")

    if not os.path.exists(input_path):
        error_msg = f"File does not exist: {input_path}"
        logger.error(f"[Request {request_id}] {error_msg}")
        return None, error_msg

    lock_file = f"{input_path}.lock"

    try:
        with FileLock(lock_file, timeout=30) as lock:
            if not lock.acquired:
                error_msg = f"Could not acquire lock for {input_path}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg

            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"[Request {request_id}] Successfully read from {input_path}")
                return data, ""
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {input_path}: {str(e)}"
        logger.error(f"[Request {request_id}] {error_msg}")
        return None, error_msg
    except Exception as e:
        error_msg = f"Error reading from {input_path}: {str(e)}"
        logger.error(f"[Request {request_id}] {error_msg}")
        return None, error_msg
