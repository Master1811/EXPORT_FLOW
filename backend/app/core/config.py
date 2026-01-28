import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # Database
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'test_database')
    
    # JWT
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_MINUTES: int = int(os.environ.get('JWT_EXPIRE_MINUTES', 1440))
    
    # CORS
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
    
    # AI
    EMERGENT_LLM_KEY: str = os.environ.get('EMERGENT_LLM_KEY', '')

settings = Settings()
