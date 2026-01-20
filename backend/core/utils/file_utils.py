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

from backend.core.infrastructure.frameworks.response_types import StandardResponse, handle_file_operations
from .logging_helpers import StandardLogger
from .constants import ErrorMessages, FileTypes

# Conditional imports based on OS
if platform.system() == "Windows":
    import msvcrt
else:
    import fcntl

logger = logging.getLogger(__name__)

class FileLock:
    def __init__(self, lock_file: str, timeout: int = 10):
        self.lock_file = lock_file
        self.timeout = timeout
        self.fd: Optional[Any] = None
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
        if self.acquired and self.fd is not None:
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

@handle_file_operations("atomic_write_json")
def atomic_write_json(data: Dict[str, Any], output_path: str) -> StandardResponse:
    """Atomically write JSON data to file with proper locking."""
    request_id = str(uuid.uuid4())
    StandardLogger.log_file_operation("atomic_write_json", request_id, output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    lock_file = f"{output_path}.lock"

    with FileLock(lock_file, timeout=30) as lock:
        if not lock.acquired:
            return StandardResponse.error_response(
                error=f"Could not acquire lock for {output_path}",
                file_path=output_path,
                lock_timeout=30
            )

        temp_dir = os.path.dirname(output_path)
        temp_prefix = f".{os.path.basename(output_path)}.tmp"

        with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, prefix=temp_prefix, delete=False) as temp_file:
            temp_path = temp_file.name
            json.dump(data, temp_file, indent=2)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, output_path)
    
    file_size = os.path.getsize(output_path)
    StandardLogger.log_file_operation("atomic_write_json", request_id, output_path, file_size)

    return StandardResponse.success_response(
        data={"file_path": output_path, "file_size": file_size},
        request_id=request_id
    )

@handle_file_operations("atomic_read_json")
def atomic_read_json(input_path: str) -> StandardResponse:
    """Atomically read JSON data from file with proper locking."""
    request_id = str(uuid.uuid4())
    StandardLogger.log_file_operation("atomic_read_json", request_id, input_path)

    if not os.path.exists(input_path):
        return StandardResponse.error_response(
            error=ErrorMessages.FILE_NOT_FOUND.format(path=input_path),
            file_path=input_path
        )

    lock_file = f"{input_path}.lock"

    with FileLock(lock_file, timeout=30) as lock:
        if not lock.acquired:
            return StandardResponse.error_response(
                error=f"Could not acquire lock for {input_path}",
                file_path=input_path,
                lock_timeout=30
            )

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        file_size = os.path.getsize(input_path)
        StandardLogger.log_file_operation("atomic_read_json", request_id, input_path, file_size)
        
        return StandardResponse.success_response(
            data=data,
            request_id=request_id,
            file_path=input_path,
            file_size=file_size
        )
