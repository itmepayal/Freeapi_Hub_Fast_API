from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # =============================
    # JWT Settings
    # =============================
    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    TEMP_TOKEN_EXPIRE_MINUTES: int = 20

    # =============================
    # Email Settings
    # =============================
    SENDGRID_API_KEY: str
    EMAIL_FROM: str
    SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID: str
    SENDGRID_PASSWORD_RESET_TEMPLATE_ID: str

    # =============================
    # Frontend
    # =============================
    FRONTEND_URL: str
    
    # =============================
    # Google OAuth
    # =============================
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # =============================
    # GitHub OAuth
    # =============================
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str
    
    # =============================
    # Session Secret 
    # =============================
    SECRET_SESSION_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
