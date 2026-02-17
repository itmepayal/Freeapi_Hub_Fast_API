from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    TEMP_TOKEN_EXPIRE_MINUTES: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
