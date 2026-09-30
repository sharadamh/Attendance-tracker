"""
Application configuration settings.
Loads environment variables from .env file using python-dotenv.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

class Config:
    """Base configuration shared by all environments."""

    # Flask secret key — used for session signing
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLAlchemy database URI; defaults to SQLite file in project root
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///attendance.db"
    )

    # Disable modification tracking (not needed, saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Configuration used during automated tests."""
    TESTING = True
    # Use an in-memory SQLite database so tests are isolated and fast
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Registry so the factory can look up configs by name
config_map = {
    "development": Config,
    "testing": TestingConfig,
    "default": Config,
}
