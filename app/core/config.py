from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True
    )
    APP_NAME: str = "AI Interview Screener"
    API_KEY: str 
    DATABASE_URL: str
    GEMINI_API_KEY: str 
    ENV_SETTING: str
    LLM_MODEL: str 
    TWILIO_ACCOUNT_SID: str 
    TWILIO_AUTH_TOKEN: str 
    TWILIO_FROM_NUMBER: str
    BASE_URL: str 
    TWILIO_RECOVERY_CODE: str

settings = Settings()