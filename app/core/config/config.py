from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET:str
    ACCESS_TOKEN_EXPIRE_MIN: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()