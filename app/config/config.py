from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool

    # Server
    HOST: str
    PORT: int

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str

    # Document
    ALLOWED_DOCUMENT_COUNT : int = 2

    # Chunking
    PARENT_CHUNK_SIZE: int = 2000      
    CHILD_CHUNK_SIZE: int = 500        
    CHILD_CHUNK_OVERLAP: int = 100 

    # Pinecone
    PINECONE_API_KEY: str 
    PINECONE_INDEX_NAME: str   

    # NVDIA-LLM-API
    NVDIA_API: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()