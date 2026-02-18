from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    TEMP_TOKEN_EXPIRE_MINUTES: int = 20

    SENDGRID_API_KEY: str
    EMAIL_FROM: str
    SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID: str
    SENDGRID_PASSWORD_RESET_TEMPLATE_ID: str
    
    FRONTEND_URL: str
    
    class Config:
        env_file = ".env"

settings = Settings()
