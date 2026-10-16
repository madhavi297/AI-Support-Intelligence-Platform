"""
Configuration module for AI Support Intelligence Platform.
Loads environment variables from .env file and provides typed settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Determine base directory (the project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from the project root if it exists
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    """
    Application settings loaded from environment variables with sensible defaults.
    """
    APP_NAME: str = os.getenv("APP_NAME", "AI Support Intelligence Platform")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database Path
    DATABASE_PATH: Path = BASE_DIR / "support_intelligence.db"

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")

    # Retrieval / RAG Settings
    EMBEDDING_MODE: str = os.getenv("EMBEDDING_MODE", "tfidf")
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "3"))

    # Project Directories
    DATA_DIR: Path = BASE_DIR / "data"
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "data" / "knowledge_base"
    MODELS_DIR: Path = BASE_DIR / "models"


# Singleton instance to be imported across modules
settings = Settings()
