"""
Configuration management for Kaggle MCP Server
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Kaggle MCP Server"""

    # Kaggle API Configuration
    KAGGLE_USERNAME: Optional[str] = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY: Optional[str] = os.getenv("KAGGLE_KEY")

    # Default download path
    DEFAULT_DOWNLOAD_PATH: str = os.getenv("KAGGLE_DOWNLOAD_PATH", "./kaggle_data")

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MCP Server configuration
    SERVER_NAME: str = "Kaggle MCP Server"
    SERVER_VERSION: str = "1.0.0"

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Cache configuration
    CACHE_TTL_COMPETITIONS: int = 3600  # 1 hour
    CACHE_TTL_DATASETS: int = 21600  # 6 hours
    CACHE_TTL_MODELS: int = 21600  # 6 hours

    @classmethod
    def validate_kaggle_credentials(cls) -> bool:
        """Check if Kaggle credentials are available"""
        # Check for kaggle.json file
        kaggle_config_path = Path.home() / ".kaggle" / "kaggle.json"
        if kaggle_config_path.exists():
            return True

        # Check for environment variables
        return bool(cls.KAGGLE_USERNAME and cls.KAGGLE_KEY)

    @classmethod
    def get_download_path(cls, custom_path: Optional[str] = None) -> str:
        """Get the download path, with optional custom override"""
        if custom_path:
            return custom_path
        return cls.DEFAULT_DOWNLOAD_PATH

    @classmethod
    def ensure_download_directory(cls, path: str) -> Path:
        """Ensure download directory exists and return Path object"""
        download_path = Path(path)
        download_path.mkdir(parents=True, exist_ok=True)
        return download_path
