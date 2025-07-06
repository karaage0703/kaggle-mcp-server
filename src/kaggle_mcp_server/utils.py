"""
Utility functions for Kaggle MCP Server
"""

import logging
import functools
from typing import Any, Dict, Callable, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


def handle_kaggle_errors(func: Callable) -> Callable:
    """Decorator to handle common Kaggle API errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in {func.__name__}: {error_msg}")

            # Map common errors to user-friendly messages
            if "401" in error_msg or "Unauthorized" in error_msg:
                return {
                    "error": "Authentication failed. Please check your Kaggle API credentials.",
                    "error_type": "authentication_error",
                }
            elif "403" in error_msg or "Forbidden" in error_msg:
                return {
                    "error": "Access denied. You may not have permission to access this resource.",
                    "error_type": "permission_error",
                }
            elif "404" in error_msg or "Not Found" in error_msg:
                return {
                    "error": "Resource not found. Please check the competition/dataset ID.",
                    "error_type": "not_found_error",
                }
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return {
                    "error": "Rate limit exceeded. Please wait before making more requests.",
                    "error_type": "rate_limit_error",
                }
            elif "timeout" in error_msg.lower():
                return {
                    "error": "Request timed out. Please try again later.",
                    "error_type": "timeout_error",
                }
            else:
                return {
                    "error": f"An unexpected error occurred: {error_msg}",
                    "error_type": "unknown_error",
                }

    return wrapper


def validate_dataset_ref(dataset_ref: str) -> tuple[bool, Optional[str]]:
    """
    Validate dataset reference format

    Args:
        dataset_ref: Dataset reference string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dataset_ref:
        return False, "Dataset reference cannot be empty"

    if "/" not in dataset_ref:
        return False, "Dataset reference must be in format 'username/dataset-name'"

    parts = dataset_ref.split("/")
    if len(parts) != 2:
        return False, "Dataset reference must contain exactly one '/' separator"

    username, dataset_name = parts
    if not username or not dataset_name:
        return False, "Both username and dataset name must be non-empty"

    return True, None


def validate_pagination_params(
    page: int, page_size: int, max_page_size: int = 100
) -> tuple[bool, Optional[str]]:
    """
    Validate pagination parameters

    Args:
        page: Page number
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        Tuple of (is_valid, error_message)
    """
    if page < 1:
        return False, "Page number must be 1 or greater"

    if page_size < 1:
        return False, "Page size must be 1 or greater"

    if page_size > max_page_size:
        return False, f"Page size cannot exceed {max_page_size}"

    return True, None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def safe_datetime_format(dt: Optional[datetime]) -> Optional[str]:
    """
    Safely format datetime to ISO string

    Args:
        dt: Datetime object or None

    Returns:
        ISO formatted string or None
    """
    if dt is None:
        return None

    try:
        return dt.isoformat()
    except Exception:
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    filename = filename.strip(" .")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    return filename


def create_success_response(
    data: Any, message: str = "Operation completed successfully"
) -> Dict[str, Any]:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Success message

    Returns:
        Standardized response dictionary
    """
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }


def create_error_response(
    error: str, error_type: str = "unknown_error"
) -> Dict[str, Any]:
    """
    Create a standardized error response

    Args:
        error: Error message
        error_type: Type of error

    Returns:
        Standardized error response dictionary
    """
    return {
        "status": "error",
        "error": error,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat(),
    }


def log_api_call(func_name: str, params: Dict[str, Any]) -> None:
    """
    Log API call for debugging and monitoring

    Args:
        func_name: Name of the function being called
        params: Parameters passed to the function
    """
    # Remove sensitive information from logging
    safe_params = {
        k: v for k, v in params.items() if k not in ["api_key", "token", "password"]
    }
    logger.info(
        f"API call: {func_name} with params: {json.dumps(safe_params, default=str)}"
    )


class KaggleAPICache:
    """Simple in-memory cache for Kaggle API responses"""

    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """
        Get cached value if it exists and is not expired

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        # Check if cache entry is expired
        if key in self._timestamps:
            age = (datetime.now() - self._timestamps[key]).total_seconds()
            if age > ttl:
                # Remove expired entry
                del self._cache[key]
                del self._timestamps[key]
                return None

        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Set cache value

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()

    def size(self) -> int:
        """Get number of cached entries"""
        return len(self._cache)


# Global cache instance
api_cache = KaggleAPICache()
