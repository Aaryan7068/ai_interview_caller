from app.core.config import settings
from app.core.database import get_db 
from app.services.llm_service import LLMService
from app.services.resume_parser import Parser
from app.services.telephony_service import TelephonyService

def get_llm_service() -> LLMService:
    
    return LLMService(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.LLM_MODEL
    )

def get_resume_parser() -> Parser:
    return Parser()

def get_telephony_service() -> TelephonyService :
    return TelephonyService(
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
        from_number=settings.TWILIO_FROM_NUMBER,
        base_url=settings.BASE_URL
    )

get_db_session = get_db