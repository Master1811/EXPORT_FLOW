import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # Database
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'test_database')
    
    # JWT - Short TTL for security
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 15))  # Short-lived access token
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))  # Longer-lived refresh token
    JWT_EXPIRE_MINUTES: int = int(os.environ.get('JWT_EXPIRE_MINUTES', 1440))  # Legacy support
    
    # Encryption
    ENCRYPTION_KEY: str = os.environ.get('ENCRYPTION_KEY', '')
    
    # CORS
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
    
    # AI
    EMERGENT_LLM_KEY: str = os.environ.get('EMERGENT_LLM_KEY', '')

settings = Settings()
