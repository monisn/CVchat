
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USER_AGENT: str = "CVchat/1.0"
    GROQ_API_KEY: str
    CONTENT_ORIGIN: str
    ALLOWED_ORIGINS: list[str]
    EXTRA_KNOWLEDGE: str = ""
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore" 
        # Pydantic Settings expects JSON format for complex types (lists, dicts) in .env
        # or we need to explicitly allow parsing.


settings = Settings()

# Set env var for LangChain/Requests user agent
os.environ["USER_AGENT"] = settings.USER_AGENT
