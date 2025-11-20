import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys with default values for testing
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-test-openai-key-123")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "gsk-test-groq-key-123") 
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "sk-test-deepseek-key-123")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIza-test-gemini-key-123")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chat.db")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Provider timeouts
    PROVIDER_TIMEOUT: int = 30
    MAX_RETRIES: int = 2

settings = Settings()